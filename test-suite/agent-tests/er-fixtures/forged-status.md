# forged-status — ER fixture

Phase marked **Status:** DONE but with a failing Acceptance claim.
Supervisor should exit 75 with STATUS_FORGED.

## Implementation surface

### Phase 1 — Falsely claimed DONE

**Status:** DONE

| File | Change |
|---|---|
| `(none)` | smoke test only |

**Acceptance:**
- `false` exits 0
