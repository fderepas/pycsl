"""Test 0506 — module-level constants in contracts (module-constants-plan).

A module-level int constant (`LIMIT = 8`) is resolved to its literal in BOTH the body and the
contract, so a `requires`/`ensures` referencing it discharges (previously a bare module name in a
contract was rejected by Module4 as `Undefined variable`). Mirrors class-body constants
(`self.CAP`). Single-assignment module names bound to an int literal are recognised; a reassigned
/ mutable global is NOT (see the boundary test 0508)."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
LIMIT = 8


#@ requires 0 <= x and x < LIMIT
#@ ensures \result == x + 1
#@ ensures \result <= LIMIT
def step(x: int) -> int:
    return x + 1
