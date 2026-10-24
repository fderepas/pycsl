r"""Test 4390 -- gen #37 route #332 (expected PASS): CONTROL: an assert WITHOUT any `no_exception` keeps the documented erasure (annotations §7.1, partial correctness, `python -O`): PROVES unchanged.
"""
# pycsl-expected: PASS
#@ ensures \result == 7
#@ assigns \nothing
def g() -> int:
    x = 1
    assert x == 2
    return 7

if __name__ == "__main__":
    try:
        print(g())
    except AssertionError:
        print("CPython raises AssertionError")
