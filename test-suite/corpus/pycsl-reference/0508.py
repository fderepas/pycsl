"""Test 0508 — module constant boundary: a reassigned (mutable) module global is NOT a constant.

`COUNTER` is assigned twice at module scope, so it is mutable global state — not a constant. It is
neither inlined nor accepted in contracts: a contract referencing it is rejected with `Undefined
variable` (module-constants-plan Q2 — a value that changes across calls has no sound meaning in
the per-function frame model; the sound path would be a `#@ ghost` mirror). Expected-FAIL = the
contract validation rejects the reference."""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
COUNTER = 0
COUNTER = 5


#@ ensures \result == COUNTER
def get_counter() -> int:
    return 5
