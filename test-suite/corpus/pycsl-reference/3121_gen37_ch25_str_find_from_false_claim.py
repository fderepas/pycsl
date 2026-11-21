r"""Test 3121 — gen #37 ch25 (expected FAIL): FALSE twin of 3120's `find_from`. On a hit Python
returns an index AT OR AFTER `start` (CPython: `"abcabc".find("c", 3) == 5`), so
`\result < start` on a hit must stay UNPROVED now that the 2-argument `find` is faithful
(non-vacuity of the seam: the op does not admit an index before `start`).
"""
# pycsl-expected: FAIL


#@ requires 0 <= start
#@ ensures \result == -1 or \result < start
#@ assigns \nothing
def find_from(s: str, sub: str, start: int) -> int:
    return s.find(sub, start)


if __name__ == "__main__":
    print(find_from("abcabc", "c", 3))
