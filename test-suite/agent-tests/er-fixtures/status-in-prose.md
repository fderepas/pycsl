# status-in-prose — ER fixture

Regression test for the start-of-line anchor in the status regex.
The phase body contains `**Status:** DONE` inside backticks and a
table cell, but NOT as a line-leading marker. The parser must NOT
treat this phase as DONE. With acceptance failing, the supervisor
must halt with `ACCEPTANCE_FAILED`, not silently accept it as
LEGACY_ACCEPTED.

## Implementation surface

### Phase 1 — Phase that talks about Status: DONE in prose

| File | Change |
|---|---|
| `(none)` | When a phase carries `**Status:** DONE` it grandfathers — see the doc. |

This phase is INTENTIONALLY open (no leading `**Status:** DONE`
marker), but its prose mentions `**Status:** DONE` to confuse a
naive parser. The acceptance below intentionally fails — if the
parser correctly identifies the phase as open, the supervisor
halts with ACCEPTANCE_FAILED. If the parser mistakenly grandfathers
the phase, it would exit 0 (silently masking the bad claim).

**Acceptance:**
- `false` exits 0
