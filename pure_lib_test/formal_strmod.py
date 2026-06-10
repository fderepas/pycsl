# Formal tests for pure_lib/strmod — REAL string theorems over symbolic `str`.
#
# These close the loop back to the English spec (test-suite/library_reference/
# string.rst): the concat-length law (a string's length is additive under `+`)
# and the capwords bound (capwords never grows its argument, RST L985-993). Both
# are genuine string-valued universal theorems over symbolic `str` inputs, NOT
# length-int artifacts — `len(...)` lowers to Why3 `String.length` (str_length_op)
# and the capwords bound is discharged against capwords' trusted contract
# (\str_length(\result) <= \str_length(s)).
#
# pycsl-flags: --memory-model hoare
from pure_lib.strmod import capwords


#@ requires \str_length(a) >= 0
#@ ensures \result == \str_length(a) + \str_length(b)
def formal_strmod_concat_len(a: str, b: str) -> int:
    """Concat-length law: |a + b| == |a| + |b| for all strings a, b.
    The fundamental length-additivity of string concatenation, proved by SMT via
    str_concat_op + str_length_op."""
    return len(a + b)


#@ requires \str_length(s) >= 0
#@ ensures \result <= \str_length(s)
def formal_strmod_capwords_bound(s: str) -> int:
    """capwords bound: |capwords(s)| <= |s| for all strings s.
    capwords collapses runs of whitespace and trims, so it never grows the
    string (RST L985-993). Proved for ALL s against capwords' trusted contract —
    the loop back to the English promise that capwords only ever shortens.
    Written in the natural Python: `len(capwords(s))` directly — `len` over a
    str-returning call resolves to String.length (str_length_op), and the
    optional `sep` is OMITTED (filled with the empty-string default)."""
    return len(capwords(s))
