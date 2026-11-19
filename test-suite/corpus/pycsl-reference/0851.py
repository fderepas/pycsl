"""Test 0851 — WL-04g NEGATIVE lock (int+str mixed literal). # pycsl-expected: FAIL

THE HEADLINE SOUNDNESS LOCK. Before WL-04g, a mixed `[1, "x"]` literal hash-coerced the
string `"x"` to a WELL-TYPED int (976090257 under PYTHONHASHSEED=0) and built `array int`,
so a contract `\result == 976090257` on `a[1]` PROVED — a claim FALSE of real Python,
where `a[1]` is the STRING "x", not the int 976090257 (SEVERITY-1 UNSOUND). WL-04g makes
the heterogeneous literal FAIL CLOSED: PyCSL now REJECTS it (no faithful `array τ` element
type — Python lists are heterogeneous, WhyML arrays are homogeneous). If this test ever
reports Verification SUCCESS, the unsound int-coercion of a mixed literal has returned.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List


#@ ensures \result == 976090257
def mixed_int_str_UNSOUND() -> int:
    a = [1, "x"]
    return a[1]
