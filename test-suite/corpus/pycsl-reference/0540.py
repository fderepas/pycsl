"""Test 0540 — parametric datatypes Option[T] (A5d).

`#@ datatype Option[T] = Nothing | Just(T)` declares a datatype with a type
PARAMETER `T`, used as a constructor payload. It lowers to a polymorphic Why3
type `type option 'a = Nothing | Just 'a`, so the SAME type works at multiple
instantiations: `Just(7)` is `option int`, `Just(s)` for a `str` is `option
string`. A monomorphic `type option = Nothing | Just int` (the pre-A5d fallback)
could not type the string use.

STATUS — PROVES (since relaunch #45). Two instantiations (int + str) give it
teeth: a monomorphic collapse to `Just int` would reject `Just(s)`.

The docstring used to say "Fails today: the `[T]` type-parameter syntax is not
in the `#@ datatype` grammar (parse error)". That was wrong on both halves. The
grammar HAS accepted `[T]` since A5d (`Module2_Parser._parse_datatype`) and
Module 6 has lowered it to a polymorphic Why3 variant since A5d
(`module6_whyml/preamble._fmt_variant`); what this file actually produced was
`[!] UNEXPECTED PIPELINE ERROR: 'str' object has no attribute 'get'` — an
INTERNAL CRASH, not a refusal. `type_params` had TWO producers under ONE key
with TWO shapes: a PEP 695 generic writes `[{"name","bound","kind"}, ...]` and a
`#@ datatype Option[T]` writes the bare names `["T", ...]`, and
`frontend/monomorphize` read the second as the first. Monomorphization is not
defined over sum types at all, so it now skips `kind == "variant"` decls.
See the negative/positive witness pair 1002/1003.
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
