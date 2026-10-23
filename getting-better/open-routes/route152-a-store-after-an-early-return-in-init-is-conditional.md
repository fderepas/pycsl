# ROUTE #152 — a top-level store AFTER an early `return` in `__init__` is conditional, and the model makes it definite

**Status: CLOSED AND FULLY GATED by gen #29 (2026-09-16), battery F' (with #153/#154). Witnesses 1513/1514.** Severity 1. Generator: carrier-rerun
(construction neighbourhood, #150's sibling).

## Measured at `8b91a93b` (CPython contradicting)

    class C:
        x = 0                       # (or `x: int = 0`)
        def __init__(self, k: int) -> None:
            if k < 0:
                return
            self.x = k
    C(-1).x      #@ ensures \result == -1   <-- PROVED; CPython 0     (record literal { x = (- 1) })

Route #83 marks a store NESTED in control flow unknown, but the store here is at the TOP LEVEL; it is
the RETURN that is nested, and it makes every statement after it conditional.

## Scoped repair (not landed)

In `_collect_init_construction`: a `return` anywhere in the constructor body (outside nested
functions/lambdas) makes the construction OPAQUE — route #150's channel (every field unknown).
Precision refinement (later): only the fields stored after the first statement containing a return.

**Battery F' (every leg predicted and hit):** emission vs the #150/#151-closed tree 1161 -> 1170 0/0/0,
python-reference and mirrors inert; conformance 38/38 + 38/38; suite 3647/3665 same 18, zero XPASS;
planes --slow 34/34. (Battery F was stopped with no verdict read to fold the match-capture carrier and #154.)
