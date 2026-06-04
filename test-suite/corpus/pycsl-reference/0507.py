"""Test 0507 — module constant (negative): a false bound over a module constant must fail.

`LIMIT = 8`; the body returns `LIMIT`, but the contract claims `\result == LIMIT + 1` — which is
`8 == 9`, unprovable. Confirms the module constant resolves to real content (its literal value),
not an opaque symbol under which a wrong bound could slip through. Expected-FAIL = the
postcondition does not discharge."""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
LIMIT = 8


#@ ensures \result == LIMIT + 1
def get_limit() -> int:
    return LIMIT
