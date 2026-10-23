r"""Test 1669 - ROUTE #190 carrier (gen #29): a NEGATIVE slice bound, reached dynamically so no literal-keyed fence can see it. Python counts a negative start from the END; Why3's `String.substring` treats `start < 0` as out of bounds and answers the EMPTY string, and the bridge asserted that answer UNCONDITIONALLY — `len(s[i:]) == 0` PROVED under `requires i == -1` while CPython returns 1. The bridge now decides only inside `0 <= lo /\ 0 <= len /\ lo + len <= length s`.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires i == 0 - 1
#@ ensures \result == 0
def probe(i: int) -> int:
    s: str = "abc"
    t: str = s[i:]
    return len(t)
