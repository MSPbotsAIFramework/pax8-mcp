# PRD-21600 · Code review

## Round 1 · 2026-10-31 · reviewed dev/PRD-21600 @ 7106eb9 (base 8d2d615)

Status: frozen @ 7106eb9

Verdict: approved

### Scope

Diff: `git diff 8d2d615...7106eb9` — `README.md` (+1 table row), `src/pax8_mcp/tools/subscriptions.py` (+16, new `pax8_get_subscription` tool), `tests/test_tools.py` (+70/-2, 3 new tests + 2 assertions added to the snapshot test), `docs/tickets/PRD-21600.{md,ac.json}` (new). No other file touched; base `8d2d615` is the repo's current `master` HEAD (no further advancement), so no re-sync was needed before this review.

### Findings

No must-fix found.

1. [suggestion] `src/pax8_mcp/tools/subscriptions.py:63` — `subscription_id` is interpolated into the path unescaped. Pre-existing pattern shared by every `*_id`-in-path tool in this module (e.g. `pax8_list_subscription_usage_summaries:86`); already flagged as a non-blocking, module-wide follow-up in the tech design's Open Questions. Not introduced by this ticket, not fixed here — agreed with the design's call to leave it.
2. [suggestion] Error returns stay as the plain `f"Error {status_code}: {message}"` string rather than a structured `{code, message, retryable}` envelope (SOP §14 "错误与网络" checklist item). This is the repo-wide shape used by all 9 pre-existing tools and the sibling PRD-21599 tool merged just before this one; changing it here would be an unrelated, cross-tool refactor and would break AC2's explicit requirement to match the existing format. Not this ticket's scope.

### Verification performed

- `uv sync && uv run pytest -v` on this worktree (synced with `master@8d2d615`): **13 passed in 1.26s**, output matches the Self-test table and `ac.json` evidence verbatim (same 13 test names/order).
- `uv run ruff check src/pax8_mcp/tools/subscriptions.py tests/test_tools.py`: `All checks passed!`.
- `uv run ruff check .`: 3 pre-existing errors, all in `__main__.py:18` / `server.py:93,99` — none in files this ticket touches. Matches the Self-test table's claimed baseline.
- `grep -rnP '[\x{4e00}-\x{9fff}]' --exclude-dir=.git --exclude-dir=.venv .`: one hit, `docs/tickets/PRD-21599-review.md:9` (pre-existing, a different ticket's review doc, already flagged there as a non-issue). No Chinese in this ticket's own diff.
- `diff <(sed -n '5,75p' README.md) ~/.claude/skills/vendor-mcp-development/reference/readme-connector-section.md`: empty — verbatim match confirmed independently.
- Read `src/pax8_mcp/api_client.py:43-51` (`Pax8Client.get`) and `tools/subscriptions.py` in full: the new tool reuses `client_factory()`, `_NO_TOKEN`, and the existing `try/except Pax8Error` shape exactly as every sibling tool does; no new credential path, no new shared/global state, no logging of tokens or responses. `pax8_update_subscription` (same file, merged by PRD-21599) is the direct precedent for this shape.
- Confirmed no orphan `tests/test_subscriptions.py` was left behind from the implementation's mid-leg test-convention switch (Self-test "Base moved during this leg" note) — `tests/` only contains `conftest.py`, `__init__.py`, `test_api_client.py`, `test_middleware.py`, `test_tools.py`.
- `mbp.py mcplock info --repo pax8-mcp`: `locked: false` — dev-lock correctly released.

### Scope, reuse, security, migrations

- Scope: confined to one tool in one existing module + README + tests + docs; matches the tech design's change list exactly, no drive-by changes to the 8 untouched tools or the client.
- Reuse: `Pax8Client.get()` unchanged and already generic; no new dependency (`respx`/`pytest-asyncio` were already declared, just newly exercised); no duplicate HTTP/client code written.
- Security: credential handling unchanged — token still resolved per-request via the existing gateway contextvar or env var; nothing new logged or persisted.
- Migrations: N/A, no database in this service.
- Cross-repo compatibility (mcp-track §1.2): N/A, single repo, no new header/field shared with another repo. `Release order: any` is correct (moot for a single-repo change).

### Fixes

N/A — no must-fix raised, nothing to fix.
