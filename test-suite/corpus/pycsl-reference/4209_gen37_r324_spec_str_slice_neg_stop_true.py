r"""Test 4209 -- gen #37 route #324 (expected PASS): CONTROL/coverage: `len(s[1:-1]) == 1` with `len(s) == 3` proves after normalisation.
"""
# pycsl-expected: PASS
#@ requires len(s) == 3
#@ ensures \result == len(s[1:-1])
#@ assigns \nothing
def f(s: str) -> int:
    return 1

if __name__ == "__main__":
    assert f("abc") == len("abc"[1:-1]), f("abc")
