# minimal-fail — ER fixture

Single open phase with a trivially-failing Acceptance claim. Supervisor
should exit 75 with ACCEPTANCE_FAILED.

## Implementation surface

### Phase 1 — Trivial fail

| File | Change |
|---|---|
| `(none)` | smoke test only |

**Acceptance:**
- `false` exits 0
