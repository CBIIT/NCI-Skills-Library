---
name: twistlock-nci
description: Query NCI's internally hosted Twistlock (Prisma Cloud Compute) console for image vulnerability/compliance scan results over the REST API. User-invoked only, via /twistlock-nci.
disable-model-invocation: true
---

# Twistlock (NCI) image scan lookup

Looks up vulnerability/compliance scan results for a container image on NCI's internal Twistlock console.

- **Requires:** VPN connectivity and Twistlock credentials.
- **Multiple repos/tags:** run steps 1–3 once, then repeat steps 4–5 per repo:tag with the same bearer token — re-authenticate (step 3) only if a query hits 401.

## Steps

1. **Resolve config.** Check env vars `TWISTLOCK_URL`, `TWISTLOCK_USER`, `TWISTLOCK_PASS`. Use `TWISTLOCK_URL` if set, otherwise default to `https://twistlock.nci.nih.gov`. For any of `TWISTLOCK_USER`/`TWISTLOCK_PASS` that are unset, prompt the user for them — do not hardcode or guess credentials.
   **Done when:** all three values are known for this run.

2. **Preflight VPN check.** Probe reachability before attempting auth, e.g. `curl -sS -m 5 -o /dev/null -w '%{http_code}' <TWISTLOCK_URL>/api/v1/_ping`. A timeout or connection refusal here means VPN is down or the host is unreachable — stop and tell the user to connect to VPN, then retry. Do not proceed to authenticate on a failed preflight.
   **Done when:** the console responds with any HTTP status (401 counts) rather than timing out or refusing.

3. **Authenticate.** `POST <TWISTLOCK_URL>/api/v1/authenticate` with JSON body `{"username": "...", "password": "..."}`. Extract `token` from the response and use it as `Authorization: Bearer <token>` on all subsequent calls. Requests must be made with TLS verification disabled (`verify=False` in requests, `-k` in curl) — the console uses NCI's internal, self-signed CA. A 401/403 here means bad credentials — re-prompt for username/password rather than retrying silently. On any later call that returns 401 (token expiry), re-authenticate once and retry that call before giving up.
   **Done when:** a valid bearer token is held for this session.

4. **Query the image.** `GET <TWISTLOCK_URL>/api/v1/registry` with query params:
   `compact=false&limit=1&offset=0&reverse=true&search=<encoded>&sort=vulnerabilityRiskScore`
   and header `Authorization: Bearer <token>`. `search` alone is sufficient — `collections`/`project` filters are optional and can be omitted for a single-image lookup. Use `/api/v1/registry` specifically — `/api/v1/scans` is a real, unrelated route on this console that returns `200` with `null`/empty for this kind of query; don't mistake it for the right endpoint.

   `<encoded>` is `repo:tag` with a specific double-encoding, not plain URL-encoding:
   ```python
   from urllib.parse import quote
   raw = f"{repo}:{tag}"
   encoded = quote(raw, safe="").replace(".", "%5C.").replace("%3A", "%253A")
   ```

   **Done when:** the raw HTTP response (status + body) has been captured.

5. **Match the exact repo/tag, then flag ambiguous-empty.** The response is a JSON array of scan result objects (not a single object) — the `search` param narrows results but does not guarantee an exact match, so filter client-side:
   ```python
   match = next(
       (r for r in results
        if r.get("repoTag", {}).get("repo") == repo
        and r.get("repoTag", {}).get("tag") == tag),
       None,
   )
   vulns = (match or {}).get("vulnerabilities") or []
   ```
   An empty `results` array, a `results` array with no matching `repoTag`, or a match with an empty `vulnerabilities` list are **not evidence of a clean scan** — each is also produced when the requesting user lacks Systems-team-granted access to that repo/tag, and Twistlock does not distinguish the cases in its response. In any of these cases, tell the user explicitly: "No scan data returned for `<repo>:<tag>` — this could mean the image hasn't been scanned yet, or that you're not authorized for this repo/tag. Confirm access with the Systems team if you expected results." Never report this as "no vulnerabilities found" on its own.
   **Done when:** a genuine `vulnerabilities` list, with fields including `cve`, `severity`, `packageName`, `packageVersion`, `status`, `cvss`, `description`, has been reported directly — or the ambiguous-empty caveat has been surfaced verbatim to the user.
