#!/usr/bin/env python3
"""cws_pm — the composite/operator skill: drive a PLAYBOOK of sub-skills, tracking + steering against the plan.

A composite skill doesn't run its own tools — it FIRES a sequence of other skills (the "caller skills")
through the governed channel, the way a top-layer project manager follows a plan and adjusts. The playbook
is data: an ordered list of steps, each `{task_id, skill, perk, vars, redeem}`. For each step this core:

  1. SKIPS it if the task is already redeemed (idempotent — reads the done-ledger v1 + v2),
  2. else fires the sub-skill's validator through govd (run_governed); a non-allow decision (e.g.
     registry_drift / blocked deps) or a non-ok step is recorded as blocked/failed,
  3. and, when the step asks, REDEEMS the task via cws-observe/redeem on that governed run's own ledger.

It steers (stop_on_fail) and reports per-step + a roll-up — the tracking layer the operator reads to adjust
the playbook. DRY_RUN validates the playbook (every skill/perk exists in the chip) WITHOUT firing.

env: PLAYBOOK, GOVD_URL (default http://127.0.0.1:5773), SWARM_DIR, DONE_LEDGER (default swarm/done-ledger.json),
GOVD_ROOT (default ~/cyberware_govd), RECORD_STORE, optional DRY_RUN, STOP_ON_FAIL. Writes two twins to
RECORD_STORE: pm.json (machine-readable, deterministic — the self-tested contract) and pm.md (the
human-readable v1.1 progress report; milestone roll-up reuses cws-observe/status's cone algorithm).
"""
from __future__ import annotations
import glob
import json
import os
import sys
from datetime import datetime

_root = os.environ.get("CYBERWARE_ROOT")
if not (_root and os.path.isdir(os.path.join(_root, "infra", "govern"))):
    _d = os.path.dirname(os.path.abspath(__file__))
    while _d != os.path.dirname(_d) and not os.path.isdir(os.path.join(_d, "infra", "govern")):
        _d = os.path.dirname(_d)
    _root = _d
if os.path.isdir(os.path.join(_root, "infra", "govern")):
    sys.path.insert(0, _root)

from infra import registry  # noqa: E402
from infra.govern import govd_client  # noqa: E402


def _redeemed(swarm):
    """task_ids with a pass entry in either done-ledger chain (v1 frozen + v2 canonical)."""
    done = set()
    for fn in ("done-ledger.json", "done-ledger-v2.json"):
        p = os.path.join(swarm, fn)
        if os.path.isfile(p):
            for e in json.load(open(p)).get("entries", []):
                if e.get("verdict") == "pass":
                    done.add(e.get("task_id"))
    return done


def _bar(num, den, w=20):
    """fixed-width text progress bar: `████░░░░` 50% (n/a when den==0; clamped at 100%)."""
    if not den:
        return "`" + "░" * w + "` n/a"
    f = min(w, round(w * num / den))                     # clamp so a bad num>den can't run the bar past full
    return "`" + "█" * f + "░" * (w - f) + f"` {min(100, round(100 * num / den))}%"


def _md(s):
    """escape a free-text value for a markdown TABLE CELL — pipes split cells, newlines break the row."""
    return str(s).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def _oneline(s):
    """flatten a free-text value for an inline prose/bullet — collapse newlines, neutralize backticks."""
    return str(s).replace("\n", " ").replace("\r", " ").replace("`", "ˋ")


def _tid(t):
    """render a task_id cell — backticked, or an em-dash when absent (never a literal `None`)."""
    return "`%s`" % t if t else "—"


def _load_dag(swarm):
    """the v1.1 task DAG keyed by task_id — the single loader shared by classification and the report."""
    dag = {}
    for p in (glob.glob(os.path.join(swarm, "P*-T*.json")) if swarm else []):
        d = json.load(open(p))
        dag[d["task_id"]] = d
    return dag


def _render_report(report, swarm, dag, redeemed, dry):
    """Render the human-facing v1.1 progress report (pm.md), the readable twin of pm.json.

    Two denominators are kept distinct: PLAYBOOK progress (over the playbook's steps) and PROGRAM
    progress (over the full DAG, per milestone). The milestone roll-up REUSES cws-observe/status's
    exact cone algorithm over the SAME `_swarm_manifest.json`, so the two never disagree — including
    `redeemed &= set(dag)` to drop off-DAG/stale ledger entries exactly as the sibling tool does. The
    only disclosed divergence: this reads done-ledger `pass` entries WITHOUT re-verifying the prev-hash
    chain (cws-observe/status does) — §6/§7 tell the reader to run that for the chain-trusted picture.
    No-emoji, pipe-`·`-separated house style; the timestamp lives only here, never in pm.json.
    """
    counts, steps = report["counts"], report["steps"]
    redeemed = redeemed & set(dag) if dag else redeemed   # DAG-scope, exactly like cws-observe/status
    manifest = {}
    mpath = os.path.join(swarm, "_swarm_manifest.json") if swarm else ""
    if mpath and os.path.isfile(mpath):
        manifest = json.load(open(mpath))
    dag_total = len(dag)

    def cone_of(gates):                              # cws-observe/status's transitive dep-cone, verbatim
        seen, stack = set(), list(gates)
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            stack += dag.get(n, {}).get("depends_on", [])
        return seen

    def title(t):
        return (dag.get(t) or {}).get("title", "")

    # milestone roll-up computed once (rendered in §2, reused in §6)
    ms = []
    for m in manifest.get("milestones", []):
        gates = m.get("gate_tasks", m.get("gate", m.get("gate_task"))) or []
        gates = [gates] if isinstance(gates, str) else gates
        cone = cone_of(gates)
        ms.append({"id": m.get("id", "?"), "label": (m.get("label") or "").strip(),
                   "rung": m.get("rung", "-"), "gates": gates,
                   "cr": len(cone & redeemed), "cl": len(cone),
                   "closed": bool(cone) and cone <= redeemed,
                   "gredeemed": all(g in redeemed for g in gates) if gates else None})

    pb_redeemed = counts["already_redeemed"] + counts["redeemed"]      # redeemed STEPS in the playbook
    total, rset = report["total"], len(redeemed)                       # playbook steps ; redeemed DAG tasks
    L = ["# cyberware v1.1 — pm report", ""]
    mode = ("Tracking pass (`DRY_RUN`): the plan classified, nothing fired." if dry
            else "Live pass: ready tasks driven through govd and redeemed on each run's own ledger.")
    L += [f"*Snapshot: {datetime.now().strftime('%Y-%m-%d')}.* {mode} "
          "Progress is redeemed, not asserted — see §7.", ""]

    # --- 1. roll-up ---
    L += ["## 1. Roll-up", "",
          f"**Status: {'ok' if counts['failed'] == 0 else 'fail'}** "
          f"({'tracking pass' if dry else 'live pass'})", "",
          f"**Playbook:** {pb_redeemed} of {total} steps redeemed — {_bar(pb_redeemed, total)}", "",
          f"**Program:** {rset} of {dag_total} DAG tasks redeemed — {_bar(rset, dag_total)}", ""]
    chip = [f"{pb_redeemed} redeemed"]
    for key, lbl in (("ran", "ran"), ("blocked_deps", "blocked:deps"),
                     ("blocked_validator", "blocked:validator"), ("failed", "failed"), ("dry", "dry")):
        if counts.get(key):
            chip.append(f"{counts[key]} {lbl}")
    L += ["`" + " · ".join(chip) + "`", "",
          f"Done-ledger: {rset} pass entries (chain not re-verified here — see §7)."]
    unprocessed = total - len(steps)                       # STOP_ON_FAIL halted the loop early -> steps < total
    if unprocessed > 0:
        L.append(f"**{unprocessed} of {total} steps were never reached** — the run halted early "
                 "(`STOP_ON_FAIL`); they appear in no section below. Re-run to drive them.")
    L.append("")

    # --- 2. milestones ---
    L += ["## 2. Milestones", ""]
    if ms:
        L += ["| milestone | rung | closure | gate | status |", "|---|---|---|---|---|"]
        for m in ms:
            gate_s = "`" + ", ".join(m["gates"]) + "`" if m["gates"] else "—"
            status = "**closed**" if m["closed"] else ("open (gate redeemed)" if m["gredeemed"] else "open")
            L.append(f"| **{m['id']}** — {_md(m['label'])} | {_md(m['rung'])} | "
                     f"{m['cr']}/{m['cl']} | {gate_s} | {status} |")
        L += ["", "_Closure is the transitive dependency cone of each milestone's gate task(s), redeemed "
              "against the done-ledger — the same roll-up `cws-observe/status` computes._", ""]
    else:
        L += ["_No milestone manifest (`_swarm_manifest.json`) under `SWARM_DIR` — program roll-up omitted._", ""]

    # --- 3. ready to pull ---
    L += ["## 3. Ready to pull", ""]
    pull = {"dry"} if dry else {"ran", "redeemed"}
    ready = sorted([s for s in steps if s["status"] in pull], key=lambda x: x["task_id"] or "")
    if ready:
        L += ["| task | validator | title |", "|---|---|---|"]
        for s in ready:
            t = s["task_id"]
            L.append(f"| {_tid(t)} | `{_md(s['skill'])}` | {_md(title(t) or s.get('perk') or '—')} |")
        L.append("")
    else:
        L += ["_Nothing ready — every remaining step is blocked (see §4)._", ""]

    # --- 4. blocked ---
    L += ["## 4. Blocked", "", "**Blocked on dependencies**", ""]
    bdeps = sorted([s for s in steps if s["status"] == "blocked:deps"], key=lambda x: x["task_id"] or "")
    if bdeps:
        L += ["| task | validator | waiting on |", "|---|---|---|"]
        for s in bdeps:
            t = s["task_id"]
            unmet = [d for d in (dag.get(t) or {}).get("depends_on", []) if d not in redeemed]
            L.append(f"| {_tid(t)} | `{_md(s['skill'])}` | {', '.join('`%s`' % d for d in unmet) or '—'} |")
        L.append("")
    else:
        L += ["_None._", ""]
    L += ["**Blocked on validator**", ""]
    bval = {}
    for s in steps:
        if s["status"] == "blocked:validator":
            bval.setdefault(s["skill"], []).append(s["task_id"])
    if bval:
        for v in sorted(bval, key=lambda x: x or ""):
            ids = ", ".join(_tid(t) for t in sorted(bval[v], key=lambda x: x or ""))
            L.append(f"- **{_tid(v)}** — not built · blocks: {ids}")
        L.append("")
    else:
        L += ["_None._", ""]

    # --- 5. what this run drove ---
    L += ["## 5. What this run drove", ""]
    if dry:
        L += ["_Tracking pass — nothing was driven. Re-run without `DRY_RUN` to drive the ready set in §3._", ""]
    else:
        driven = [s for s in steps if s["status"] in ("ran", "redeemed", "failed")]
        if driven:
            L += ["| task | result | run_id |", "|---|---|---|"]
            label = {"redeemed": "redeemed", "ran": "ran (not redeemed)", "failed": "**failed**"}
            for s in driven:
                rid = "`%s`" % s["run_id"] if s.get("run_id") else "—"
                L.append(f"| {_tid(s['task_id'])} | {label[s['status']]} | {rid} |")
            nred = sum(s["status"] == "redeemed" for s in driven)
            nran = sum(s["status"] == "ran" for s in driven)
            nfail = sum(s["status"] == "failed" for s in driven)
            L += ["", f"`{nred} redeemed · {nran} ran · {nfail} failed` this pass.", ""]
            for s in driven:
                if s["status"] == "failed":
                    L.append(f"- **{_tid(s['task_id'])} failed** — {_oneline(s.get('detail', ''))}")
            if nfail:
                L.append("")
        else:
            L += ["_Nothing was driven this pass._", ""]

    # --- 6. honest status ---
    L += ["## 6. Honest status — what is not yet redeemed", ""]
    if counts["blocked_validator"]:
        L.append(f"- **{counts['blocked_validator']} steps blocked on unbuilt validators** — "
                 "the validator skill must be authored before its tasks can be driven (§4).")
    if counts["blocked_deps"]:
        L.append(f"- **{counts['blocked_deps']} steps blocked on dependencies** — upstream tasks must redeem first (§4).")
    open_ms = [m["id"] for m in ms if not m["closed"]]
    if open_ms:
        L.append(f"- **Open milestones:** {', '.join(open_ms)} — the spine still ahead (§2 has the closure ratios).")
    L.append("- **Chain caveat:** this report reads done-ledger `pass` entries without re-verifying the "
             "prev-hash chain; `cws-observe/status` re-verifies the chain — run it for the chain-trusted picture.")
    if not dry and counts["failed"]:
        L.append(f"- **{counts['failed']} step(s) failed this pass** (§5).")
    if (report["total"] - len(steps)) > 0:
        L.append(f"- **{report['total'] - len(steps)} step(s) never reached** — the run halted early "
                 "(`STOP_ON_FAIL`); re-run to drive them.")
    L.append("")

    # --- 7. verify it yourself ---
    L += ["## 7. Verify it yourself", "", "```sh",
          "# the chain-verified milestone picture (re-verifies the done-ledger prev-hash chain)",
          "python3 -m infra.tool.skilltest --skill cws-observe --perk status",
          "# the cws-pm self-test (asserts pm.json)",
          "python3 -m infra.tool.skilltest --skill cws-pm --perk run",
          "# re-render this board without firing",
          "PLAYBOOK=<playbook> SWARM_DIR=<swarm> DRY_RUN=1 RECORD_STORE=<dir> python3 cws_pm.py",
          "```", "",
          "`pm.json` is the machine-readable twin of this report — same data, asserted by the self-test."]
    return "\n".join(L) + "\n"


def main() -> int:
    store = os.environ["RECORD_STORE"].rstrip("/")
    out = os.path.join(store, "pm.json")
    os.makedirs(store, exist_ok=True)
    playbook = json.load(open(os.environ["PLAYBOOK"]))
    steps = playbook if isinstance(playbook, list) else playbook.get("steps", [])
    govd = os.environ.get("GOVD_URL", "http://127.0.0.1:5773")
    swarm = os.environ.get("SWARM_DIR", "")
    done_ledger = os.environ.get("DONE_LEDGER") or (os.path.join(swarm, "done-ledger.json") if swarm else "")
    govd_root = os.path.expanduser(os.environ.get("GOVD_ROOT", "~/cyberware_govd"))
    dry = os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes")
    stop_on_fail = os.environ.get("STOP_ON_FAIL", "").lower() in ("1", "true", "yes")

    dag = _load_dag(swarm)                                 # single DAG loader, shared with the report
    redeemed = _redeemed(swarm) if swarm else set()
    if dag:
        redeemed &= set(dag)                              # DAG-scope, exactly like cws-observe/status
    results = []
    counts = {"already_redeemed": 0, "redeemed": 0, "ran": 0,
              "blocked_deps": 0, "blocked_validator": 0, "failed": 0, "dry": 0}

    def deps_of(tid):
        return (dag.get(tid) or {}).get("depends_on", [])

    for st in steps:
        tid, skill, perk = st.get("task_id"), st.get("skill"), st.get("perk")
        rec = {"task_id": tid, "skill": skill, "perk": perk}
        # --- TRACK: classify each task against the plan before driving anything ---
        if tid and tid in redeemed:
            rec["status"] = "redeemed"; rec["detail"] = "already redeemed"
            counts["already_redeemed"] += 1; results.append(rec); continue
        if not os.path.isdir(registry.skill_dir(skill or "")):
            rec["status"] = "blocked:validator"; rec["detail"] = f"validator not built: {skill}"
            counts["blocked_validator"] += 1; results.append(rec); continue
        unmet = [d for d in deps_of(tid) if d not in redeemed]
        if unmet:
            rec["status"] = "blocked:deps"; rec["detail"] = f"deps not redeemed: {unmet}"
            counts["blocked_deps"] += 1; results.append(rec); continue
        if dry:
            rec["status"] = "dry"; rec["detail"] = "ready — would fire"; counts["dry"] += 1
            results.append(rec); continue
        # --- DRIVE: this task is ready -> fire its validator through govd, then redeem on that run ---
        rs = os.path.join(store, f"step-{tid or skill}"); os.makedirs(rs, exist_ok=True)
        r = govd_client.run_governed(govd, {"skill": skill, "perk": perk, "record_store": rs, "vars": st.get("vars", {})})
        if r.get("decision") != "allow" or r.get("error") or \
           any(s.get("exit") not in (0, None) for s in r.get("results", [])):
            rec["status"] = "failed"; rec["detail"] = r.get("error") or f"decision={r.get('decision')} steps={r.get('results')}"
            counts["failed"] += 1; results.append(rec)
            if stop_on_fail:
                break
            continue
        rec["status"] = "ran"; rec["run_id"] = r.get("run_id"); counts["ran"] += 1
        if st.get("redeem") and tid and swarm:                # redeem on THIS governed run's own ledger
            evidence = os.path.join(govd_root, r["run_id"], "ledger.json")
            govd_client.run_governed(govd, {"skill": "cws-observe", "perk": "redeem",
                 "record_store": os.path.join(rs, "redeem"),
                 "vars": {"SWARM_DIR": swarm, "TASK_ID": tid, "RUN_LEDGER": evidence, "DONE_LEDGER": done_ledger}})
            rp = os.path.join(rs, "redeem", "redeem.json")
            redj = json.load(open(rp)) if os.path.isfile(rp) else {}
            if redj.get("verdict") == "pass":
                rec["status"] = "redeemed"; counts["ran"] -= 1; counts["redeemed"] += 1
                redeemed.add(tid)                            # so a downstream ready task cascades this run
            else:
                rec["redeem"] = redj.get("verdict"); rec["detail"] = redj.get("reason", "")
        results.append(rec)

    status = "ok" if counts["failed"] == 0 else "fail"     # blocked is a tracked state, not a failure
    report = {"status": status, "dry_run": dry, "total": len(steps), "redeemed_total": len(redeemed),
              "counts": counts, "steps": results}
    json.dump(report, open(out, "w"), indent=2)
    md = os.path.join(store, "pm.md")                      # the human-readable twin (timestamp lives ONLY here)
    try:                                                   # a cosmetic render must never fail the governed run
        open(md, "w").write(_render_report(report, swarm, dag, redeemed, dry))
    except Exception as e:
        open(md, "w").write(f"# cyberware v1.1 — pm report\n\n_Report render failed: {e}. "
                            "See `pm.json` for the machine-readable status._\n")
    print(json.dumps({"tool": "cws_pm", "status": status, "counts": counts, "report": out, "md": md}))
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
