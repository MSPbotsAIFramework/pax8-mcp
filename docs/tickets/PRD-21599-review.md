# PRD-21599 · Code review

## Round 1 · 2026-10-31 · reviewed dev/PRD-21599 @ c419fc5 (base f71ce7a)

Verdict: approved

### Findings

1. [suggestion] docs/tickets/PRD-21599.md:269 — the Self-test table cites the SOP section name in Chinese ("有就跑", quoted verbatim from the skill's own SOP to justify skipping `gitleaks detect` when the binary is unavailable). This is a direct quote of the reference material's section title, not code or the shipped README; it does not affect runtime behavior, the connector's user-facing docs, or BA acceptance. Flagged because the repo-wide "no Chinese anywhere" rule (SOP §0.4) is otherwise fully met — the self-test's own claim of "No output (no Chinese anywhere in the repo)" is technically one character-class match short of literally true. No action required; worth a one-word English paraphrase ("skip-if-unavailable") next time this citation pattern is used.

### Verification performed

- `uv sync && uv run pytest -v`: 10/10 passed (reran independently in a fresh worktree, matches the Self-test table).
- `uv run ruff check src/pax8_mcp/api_client.py src/pax8_mcp/tools/subscriptions.py tests/`: clean. `uv run ruff check .`: same 3 pre-existing errors (`__main__.py:18`, `server.py:93`, `server.py:99`), none in touched files — confirmed baseline-red by file/line, not just count.
- `grep -rnP '[\x{4e00}-\x{9fff}]' --exclude-dir=.git --exclude-dir=.venv .`: one hit, see Finding 1 (docs only, not code or README).
- README lines 5-75 vs `vendor-mcp-development/reference/readme-connector-section.md`: byte-identical (`diff` empty).
- Local HTTP smoke (`MCP_TRANSPORT=http AUTH_MODE=gateway`): `/health` → 200; `POST /mcp` without `X-Pax8-Token` → 401 with `required_headers: ["X-Pax8-Token"]`; `initialize` with placeholder header → 200 JSON-RPC result. Matches the Self-test table's SOP §12 claims.
- Read `src/pax8_mcp/api_client.py` `_clean_params`: filters on `v is not None` (not truthiness), so `put()` correctly drops only unset optional fields and would not drop a legitimate `0`/`""`/`[]` value — confirms AC2 is implemented correctly, not just asserted by the test.
- `tests/test_middleware.py::test_concurrent_update_calls_do_not_leak_credentials_across_tenants` drives two real concurrent requests through the ASGI app with `asyncio.gather` and two different `X-Pax8-Token` headers, then asserts each outbound Pax8 `PUT` carried only its own tenant's token — a genuine concurrency test for AC5, not two sequential calls dressed up as concurrent.
- `git diff --stat f71ce7a...c419fc5`: only `README.md`, `api_client.py`, `subscriptions.py`, and new `tests/` files changed. No touch to `server.py`, `config.py`, `__main__.py`, `pyproject.toml`, `uv.lock`, or `Dockerfile` — matches the tech design's "no new dependency, no other files" claim.
- Commit authorship (`git log f71ce7a..c419fc5`): all 5 commits author+committer `Dev01.MBAgent <dev01.mbagent@mspbots.ai>` — correct per `mcp-track.md` §4.7.
- `origin/master` still at `f71ce7a` at review time — the `[DEV]` stub's synced base is still current, no re-sync needed before merge.
- `ticket_store.py validate --ac docs/tickets/PRD-21599.ac.json`: ledger OK, 7 cases.

### REVIEW.md BLOCKER checklist

No schema/migration (N/A for this repo), no `--force` push, no mspack/release-branch contact, no DROP, no unresolved merge conflicts (none occurred), base (`master`) confirmed current at review time, no reuse/dependency violations (reused `_clean_params`/`_headers`/`_raise_for_status`/`client_factory` pattern; no new runtime dependency). No BLOCKER conditions met.

Status: frozen @ c419fc5
