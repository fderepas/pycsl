r"""Test 4210 -- gen #37 route #324 (expected PASS): CONTROL/coverage: `len(s[-2:3]) == 2` proves after normalisation.
"""
# pycsl-expected: PASS
#@ requires len(s) == 3
#@ ensures \result == len(s[-2:3])
#@ assigns \nothing
def f(s: str) -> int:
    return 2

if __name__ == "__main__":
    assert f("abc") == len("abc"[-2:3]), f("abc")
