# forbidden-rm — ER fixture

Open phase with an Acceptance claim invoking `rm` (a forbidden token —
acceptance must be read-only). Supervisor should exit 75 with
CLAIM_REJECTED.

## Implementation surface

### Phase 1 — Phase with a dangerous acceptance claim

| File | Change |
|---|---|
| `(none)` | smoke test only |

**Acceptance:**
- `rm /tmp/some-file` exits 0
