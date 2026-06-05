"""Test 0535 — or-patterns over constructors (A5c, `case A() | B():`).

A match arm may combine constructors with `|`: `case Red() | Green():`. Fails
today: the constructor-match lowering renders a single `Constructor`/`Wildcard`
per arm, so an `Or` pattern collapses to a wildcard `_` — catching EVERYTHING,
including `Blue()`. With the subject `Blue()` and `ensures \\result == 0`, a
correct or-pattern routes Blue to the `Blue()` arm (returns 0); the broken
collapse `| _ -> 1` catches Blue and returns 1, contradicting the contract.
Flips when Why3's native or-pattern `| Red | Green -> …` is emitted.
"""
#@ datatype Color = Red | Green | Blue
_ = 0  # anchor


#@ ensures \result == 0
#@ assigns \nothing
def is_red_or_green() -> int:
    c = Blue
    match c:
        case Red() | Green():
            return 1
        case Blue():
            return 0
