r"""Test 3753 -- gen #37 ch34 (expected FAIL): false twin of 3752: "xxab".startswith("ab", 1) is False in CPython (the occurrence is at index 2), so claiming 1 must NOT prove.
"""
# pycsl-expected: FAIL


#@ requires s == "xxab"
#@ ensures \result == 1
#@ assigns \nothing
def at_one(s: str) -> int:
    if s.startswith("ab", 1):
        return 1
    return 0
