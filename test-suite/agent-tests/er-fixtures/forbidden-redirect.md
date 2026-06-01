# forbidden-redirect — ER fixture

Phase with an Acceptance claim that uses output redirect (`>`).
Supervisor should exit 75 with CLAIM_REJECTED.

## Implementation surface

### Phase 1 — Phase with output redirect

| File | Change |
|---|---|
| `(none)` | smoke test only |

**Acceptance:**
- `echo hi > /tmp/something` exits 0
