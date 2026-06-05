"""Test 0540 — parametric datatypes Option[T] (A5d).

`#@ datatype Option[T] = Nothing | Just(T)` declares a datatype with a type
PARAMETER `T`, used as a constructor payload. It lowers to a polymorphic Why3
type `type option 'a = Nothing | Just 'a`, so the SAME type works at multiple
instantiations: `Just(7)` is `option int`, `Just(s)` for a `str` is `option
string`. A monomorphic `type option = Nothing | Just int` (the pre-A5d fallback)
could not type the string use.

Fails today: the `[T]` type-parameter syntax is not in the `#@ datatype` grammar
(parse error). Flips when the type parameter threads through to a polymorphic
Why3 variant. Two instantiations (int + str) give it teeth — a monomorphic
collapse to `Just int` would reject `Just(s)`.
"""
#@ datatype Option[T] = Nothing | Just(T)
_ = 0  # anchor


#@ ensures \result == 7
#@ assigns \nothing
def use_int() -> int:
    o = Just(7)
    match o:
        case Just(n):
            return n
        case Nothing():
            return 0


#@ ensures \str_length(\result) == \str_length(s)
#@ assigns \nothing
def use_str(s: str) -> str:
    o = Just(s)
    match o:
        case Just(v):
            return v
        case Nothing():
            return ""
