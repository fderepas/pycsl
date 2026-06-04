"""Test 0481 — strings: __add__ (`s + t`, concatenation).

`+` on runtime `str` is string concatenation (was nonsensical int-add). PROVES as of
strings-plan Stage 2: `+` over string operands lowers to Why3 `concat` — in a spec the logic
`concat` (also the `^` operator), and in a program (body) context a `val str_concat_op`
bridge tied to `concat`. The concat-length-additivity postcondition discharges under SMT."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0 and \str_length(t) >= 0
#@ ensures \str_length(\result) == \str_length(s) + \str_length(t)
#@ ensures \result == s ^ t
#@ assigns \nothing
def cat(s: str, t: str) -> str:
    return s + t
