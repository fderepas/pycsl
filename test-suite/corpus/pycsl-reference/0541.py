"""Test 0541 — match captures referenced in contracts, via projectors (A5b).

A `case`-bound capture (`case Val(n):`) is scoped to its arm, so a function-level
`#@ ensures` cannot name it. A5b adds two CONSTRUCTOR-PROJECTOR spec operators
that reference a variant's payload directly in a contract, with no match:
  - `\is_ctor(x, Ctor)` — true iff `x` was built with constructor `Ctor`
    (lowers to `match x with Ctor _ … -> true | _ -> false`).
  - `\payload(x, Ctor)` — the (sole) payload of `x` viewed as `Ctor`
    (lowers to `match x with Ctor v -> v | _ -> <default>`).

So `unwrap` can specify its result in terms of the payload at the function level:
under `\is_ctor(b, Val)` the body returns `n` where `b = Val(n)`, which is exactly
`\payload(b, Val)`. Fails today: neither operator is in the contract grammar
(parse error). Flips when they are wired Module2→5→6.
"""
#@ datatype Box = Empty | Val(int)
_ = 0  # anchor


#@ requires \is_ctor(b, Val)
#@ ensures \result == \payload(b, Val)
#@ assigns \nothing
def unwrap(b: Box) -> int:
    match b:
        case Val(n):
            return n
        case Empty():
            return -1
