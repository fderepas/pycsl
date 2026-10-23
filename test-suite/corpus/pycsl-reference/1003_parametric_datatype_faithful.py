"""Test 1003 — POSITIVE witness for the parametric `#@ datatype` (A5d) lowering.

The true-contract half of the `1002` pair. `#@ datatype Option[T]` lowers to the
POLYMORPHIC Why3 variant `type option 'a = Nothing | Just 'a`
(`module6_whyml/preamble._fmt_variant`), so the SAME declared type carries an
`int` payload in `use_int` and a `str` payload in `use_str`. A monomorphic
collapse to `Just int` would reject the second.

This file CRASHED before relaunch #45 — `[!] UNEXPECTED PIPELINE ERROR: 'str'
object has no attribute 'get'` — because `frontend/monomorphize` read the variant
decl's bare-name `type_params` as the PEP 695 dict shape. It is the flip witness:
at the parent commit it does not verify (it does not even emit); at HEAD it does.
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
