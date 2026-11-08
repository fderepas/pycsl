r"""Test 4211 -- gen #37 route #324 (expected PASS): CONTROL/coverage: `len(s[-10:2]) == 2` (bound clamps to 0, CPython 2) proves.
"""
# pycsl-expected: PASS
#@ requires len(s) == 3
#@ ensures \result == len(s[-10:2])
#@ assigns \nothing
def f(s: str) -> int:
    return 2

if __name__ == "__main__":
    assert f("abc") == len("abc"[-10:2]), f("abc")
