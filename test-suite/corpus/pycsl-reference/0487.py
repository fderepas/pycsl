"""Test 0487 — strings: __repr__ (`repr(s)`).
Target: repr() adds surrounding quotes; the content transform is NOT modeled (opaque). The
naive `len(repr(s)) == len(s) + 2` is UNSOUND in general — Python adds exactly 2 quote chars
ONLY for quote/escape-free strings (otherwise escapes lengthen it further), so PyCSL does NOT
emit that equality. The faithful, sound fact is the LOWER bound: repr of any str always carries
at least its two surrounding quote characters, so `\str_length(repr(s)) >= 2`. `repr` lowers to
the abstract `val str_repr_op` whose only `ensures` is exactly `String.length result >= 2`."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0
#@ ensures \str_length(\result) >= 2
#@ assigns \nothing
def torepr(s: str) -> str:
    return repr(s)
