---
skill: cws-pm
name: Composite Operator (PM)
perks: [run]
---

# cws-pm — composite operator / automated project manager

The top-layer operator. A **composite** skill runs no tools of its own — it FIRES a sequence of other
skills (the playbook's "caller skills") through the governed channel, the way a project manager follows a
plan and adjusts. It is the steering + tracking layer over [[cws-observe]] (which records progress) and the
validator skills (which do the gating).

## What to look out for
`pm.json` carries `{status, dry_run, total, counts:{redeemed,skipped,failed,blocked,dry}, steps[]}`. Each
step reports `ran` / `redeemed` / `skipped` (already redeemed) / `blocked` (non-allow, e.g. registry_drift
or unmet deps) / `failed`. The operator reads this to adjust the playbook.

## Perks
| perk | tool | nature |
|---|---|---|
| `run` | `cws_pm` | drive a playbook of sub-skills via govd: skip-if-redeemed, fire the validator, optionally redeem via cws-observe, steer (STOP_ON_FAIL) — needs a running govd |

- **`run`** — set `PLAYBOOK` (JSON list of `{task_id, skill, perk, vars, redeem}`) + optional `SWARM_DIR`/`DONE_LEDGER` (skip-if-redeemed + redemption), `DRY_RUN`, `STOP_ON_FAIL`. Output: `pm.json`.

## How it composes
The playbook is data — the plan as a list of governed sub-skill calls. `cws-pm/run` drives the redeemable
steps end-to-end and reports what's blocked-on-construction; the operator edits the playbook (adds steps,
fixes vars, builds a subject) and re-runs. It cannot author a subject — that is the agent's creative work.
