# PRD-21601 · Code review

Status: frozen @ e1f94c4

## Round 1 · 2026-10-31 · reviewed dev/PRD-21601 @ e1f94c4 (base master @ 8d2d615)

Verdict: approved

### Scope

`git diff origin/master...e1f94c4` touches exactly 4 files: `src/pax8_mcp/tools/products.py`, `tests/test_products.py` (new), `tests/test_tools.py`, `README.md`. This matches the tech design's Change list in `docs/tickets/PRD-21601.md` exactly — no scope creep.

### Findings

No must-fix, no suggestions.

Checked against `references/REVIEW.md` §2 and `mcp-track.md` §4.3:

1. **Correctness** — `pax8_get_product` (`src/pax8_mcp/tools/products.py:47-61`) is a line-for-line copy of the established control flow used by all 9 pre-existing tools (`client_factory()` null check → `_NO_TOKEN`, `try/except Pax8Error` → `f"Error {e.status_code}: {e.message}"`). `Pax8Client.get()` (`src/pax8_mcp/api_client.py:43-51`) is unmodified and generic over path, so `f"/products/{product_id}"` needs no new client code.
2. **Credential handling** — `Pax8Error.message` is built only from the vendor response body/text (`api_client.py:62-68`); it never includes the `Authorization` header, so the error path cannot leak the caller's token. Verified by `tests/test_products.py::test_get_product_error_does_not_leak_token`.
3. **Per-request isolation** — the new tool reuses `client_factory()` / `_gateway_token_var` contextvar isolation (`server.py:19-33`), unmodified. `tests/test_products.py::test_get_product_concurrent_requests_do_not_share_token` runs two concurrent calls with two different tokens via `asyncio.gather` and asserts each outbound request carried only its own `Authorization` header — this is real evidence for AC5, not just an assumption.
4. **Schema validation** — `test_get_product_requires_product_id` asserts `ToolError` is raised and the mocked route is never called when `product_id` is omitted, confirming AC4 (reject-before-call) with a required, no-default parameter.
5. **Test file layout changed from the tech design (`tests/tools/test_products.py`) to `tests/test_products.py`** — Self-test explains this: `tests/` didn't exist yet when the design was written at `f71ce7a`; PRD-21599 added `tests/` with a flat layout in the meantime (merged into this branch at `2ea4053`), and the dev leg correctly followed the repo's actual established convention instead of the design's stale assumption. This is a technical-design-level detail (file layout, not AC content) that the dev leg owns per `handoff.md`'s three-artifact split; it does not need a design return trip.
6. **Gates reproduced independently** (not just trusting the Self-test section): `uv sync && uv run pytest -q` → 16 passed on `e1f94c4`; `uv run ruff check src/pax8_mcp/tools/products.py tests/test_products.py tests/test_tools.py` → all checks passed; `uv run ruff check .` → 3 pre-existing errors, all in `server.py`/`__main__.py` (last touched at `dffa35b`, months before this ticket, not in this ticket's change list) — correctly recorded as a pre-existing WARN, not a regression.
7. **README** — Tool List table has exactly one new row for `pax8_get_product`; the `## MSPbots Connector` section (lines 5-75) is byte-for-byte identical to `~/.claude/skills/vendor-mcp-development/reference/readme-connector-section.md` (diffed directly, confirmed).
8. **No Chinese** in any file this ticket touches (`grep -rnP '[\x{4e00}-\x{9fff}]'` on the 4 changed files → no output). The one pre-existing hit in the repo (`PRD-21599.md`/`PRD-21599-review.md`, a quoted Chinese SOP section title) is unrelated and already accepted in that ticket's own review.
9. **No new dependency**; `respx` used in the new tests is already a dev dependency (`pyproject.toml`).
10. **Backward compatibility** — purely additive; the 8 pre-existing tools' tests (added by PRD-21599, now part of this branch) still pass unchanged alongside the 6 new ones (16/16).

Conclusion: this is a minimal, pattern-following addition with real concurrency and error-leak test evidence for the two ACs (AC5, AC2) that are easiest to get wrong in a shared-credential MCP connector. Approved for merge.
