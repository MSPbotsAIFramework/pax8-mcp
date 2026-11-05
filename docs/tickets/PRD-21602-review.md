# PRD-21602 · Code review

Status: frozen @ 1a3e794

## Round 1 · 2026-11-05 · reviewed dev/PRD-21602 @ 75966b1 (base master @ 2f5137b)

Verdict: approved

### Findings

No must-fix findings.

1. [suggestion] `src/pax8_mcp/tools/companies.py:68-78` — `pax8_get_company` returns the plain `f"Error {status_code}: {message}"` string and `json.dumps(result, indent=2)` rather than the SOP §14 structured error envelope (`code`/`message`/`retryable`) or an `ensure_ascii=False`/no-`indent` serialization. This mirrors the exact convention already used by all 9 pre-existing tools in this repo (including the other two functions in the same file) and the three sibling tickets (PRD-21599/21600/21601) already merged into `master` with the same shape; PRD-21600's review already flagged the error-envelope point as a repo-wide, out-of-scope concern for a single-tool ticket. Changing it here would be an unrelated cross-tool refactor touching all 9 tools, not something this ticket's scope covers. Not blocking.
2. [suggestion] `src/pax8_mcp/tools/companies.py:64` — no `readOnlyHint` annotation on the new tool. Consistent with the other two (pre-existing) read tools in this same file, which also have no hints; only the one write tool in the repo (`pax8_update_subscription`) carries hints. Retrofitting hints repo-wide is out of scope for this ticket.

### Verification performed

- `uv sync && uv run pytest -q` at `75966b1`: 23 passed (matches the `[DEV]` stub's claim).
- `uv run ruff check .`: same 3 pre-existing errors (`__main__.py:18`, `server.py:93`, `server.py:99`), 0 new; `src/pax8_mcp/tools/companies.py` and the new test files are clean.
- Chinese-character scan (`grep -rnP '[\x{4e00}-\x{9fff}]' --exclude-dir=.git --exclude-dir=.venv .`): all hits are verbatim quotes inside `docs/tickets/*.md` ticket documents; none in `src/`, `tests/`, or `README.md`.
- README "MSPbots Connector" section (`sed -n '5,75p' README.md`) diffed byte-for-byte against `vendor-mcp-development` skill's `reference/readme-connector-section.md`: identical. Pre-existing, untouched by this ticket.
- Code review of `src/pax8_mcp/tools/companies.py`: `pax8_get_company` follows the exact same shape as the adjacent `pax8_list_company_contacts` (client_factory → `_NO_TOKEN` guard → `client.get()` → `Pax8Error` → structured-ish error string). No new dependency, no client change, no credential-handling change — still per-request via `client_factory()`/`contextvars`, nothing cached or logged.
- Scope: change is additive and isolated to `companies.py` + `README.md` Tool List row + new `tests/` files. No other tool's behavior touched. Matches the tech design in `docs/tickets/PRD-21602.md`.
- `git fetch origin master` at review time: still `2f5137b`, same as the `[DEV]` stub's synced base — no re-sync needed before merge.
