r"""Test 4208 -- gen #37 route #324 (expected PASS): CONTROL: `len(s[0:2]) == 2` (non-negative literal bounds, raw substring) proves.
"""
# pycsl-expected: PASS
#@ requires len(s) == 3
#@ ensures \result == len(s[0:2])
#@ assigns \nothing
def f(s: str) -> int:
    return 2

if __name__ == "__main__":
    assert f("abc") == len("abc"[0:2]), f("abc")
