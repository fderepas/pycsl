r"""Test 1705 - ROUTE #203 carrier (gen #30): a SINGLE-part f-string was the part itself. `s = f"{n}"` with `n = 5` emitted `s := !n`, so `s == "5"` compared `!s = 1359629258` (the hash of the literal `"5"`) against 5 and DECIDED FALSE - this contract PROVED while CPython answers 1, because `f"{5}"` IS `"5"`. The TRUE twin was REFUSED. A wrong DECISION, not a merely-unknown value. Every OTHER shape the int-model f-string joiner produces was already opaque: a multi-part f-string is wrapped in `str_concat` (an abstract op with no axioms) and a string-typed part goes through `str_hash_op`; only the single-part non-string case escaped raw. It now answers a VALUE-KEYED opaque, so two equal `n`s still give equal strings and no literal's hash is provably equal to it. This file must FAIL.
"""
# pycsl-expected: FAIL

_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    n = 5
    s = f"{n}"
    if s == "5":
        return 1
    return 2
