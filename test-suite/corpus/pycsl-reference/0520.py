"""Test 0520 — sum types: nullary enum + exhaustive pattern match.

A `#@ datatype` directive declares a Why3 algebraic type whose nullary constructors lower to a real
`type color = Red | Green | Blue`. A `match` over the value lowers to a Why3 `match c with | Red ->
... end`, so exhaustiveness is checked by the solver (no missing/extra case) and each arm's
postcondition discharges — not an opaque int coarsening of the enum."""
#@ datatype Color = Red | Green | Blue
_ = 0  # anchor


#@ ensures \result >= 0 and \result <= 2
def to_code(c: Color) -> int:
    match c:
        case Red():
            return 0
        case Green():
            return 1
        case Blue():
            return 2
