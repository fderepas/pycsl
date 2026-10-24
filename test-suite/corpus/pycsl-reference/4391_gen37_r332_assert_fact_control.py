r"""Test 4391 -- gen #37 route #332 (expected PASS): CONTROL: a true assert under `no_exception \all` on a branch (`assert n >= 4` under `n > 3`) PROVES.
"""
# pycsl-expected: PASS
#@ requires n >= 0
#@ ensures \result >= 0
#@ assigns \nothing
#@ no_exception \all
def g(n: int) -> int:
    if n > 3:
        assert n >= 4
        return n - 4
    return 0

if __name__ == "__main__":
    try:
        print(g(5))
    except AssertionError:
        print("CPython raises AssertionError")
