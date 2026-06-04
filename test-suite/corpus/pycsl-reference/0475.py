"""Test 0475 — strings: __eq__ (`s == t`, content equality).

Content equality on runtime `str`, replacing the unsound int-hash identity. PROVES as of
strings-plan Stage 2: in a spec, `s == t` is the polymorphic Why3 `=` on strings; in a
program (body) context it bridges through `val str_eq_op : bool` (the logic `=` is not
usable as a program value). Written in if-form because returning a comparison directly
(`return s == t`) hits a pre-existing bool-vs-int return-coercion gap that is orthogonal to
strings (it affects int comparisons too)."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0
#@ ensures (s == t) ==> \result == 1
#@ ensures (s != t) ==> \result == 0
#@ assigns \nothing
def streq(s: str, t: str) -> int:
    if s == t:
        return 1
    return 0
