r"""Test 3122 — gen #37 ch25 (expected FAIL): FALSE twin of 3120's `find_from`. A hit can run
right up to the end of the receiver (CPython: `"abc".find("c", 1) == 2`, and 2 + len("c") ==
len("abc")), so the strict `\result + len(sub) < len(s)` must stay UNPROVED: the faithful op
bounds the hit by the receiver's length, it does not invent a tighter bound.
"""
# pycsl-expected: FAIL


#@ requires 0 <= start
#@ ensures \result == -1 or \result + len(sub) < len(s)
#@ assigns \nothing
def find_from(s: str, sub: str, start: int) -> int:
    return s.find(sub, start)


if __name__ == "__main__":
    print(find_from("abc", "c", 1))
