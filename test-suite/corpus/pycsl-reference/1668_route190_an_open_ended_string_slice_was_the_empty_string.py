r"""Test 1668 - ROUTE #190 (gen #29): an OMITTED slice bound is carried in the typed IR as a `None` EXPRESSION, not an absent key, so the length fallback every branch of the slice handler writes was dead code and the bound lowered to the integer 0. `"abc"[1:]` emitted `str_sub_op s 1 ((0) - (1))` — a NEGATIVE length — and Why3's `String.substring` answers the EMPTY string for that, so `len(t) == 0` PROVED while CPython returns 2.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    s: str = "abc"
    t: str = s[1:]
    return len(t)
