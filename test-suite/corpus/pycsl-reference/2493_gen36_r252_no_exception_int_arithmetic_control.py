r"""Test 2493 — route #252 (expected PASS): CONTROL: under `#@ no_exception \all`, arithmetic and
comparison on `int` parameters stay exception-free.
"""
# pycsl-expected: PASS


#@ no_exception \all
#@ ensures \result == 1
#@ assigns \nothing
def f(x: int, y: int) -> int:
    z = -x + (x - y)
    if x < y or x == y:
        return 1
    return 1


if __name__ == "__main__":
    assert f(1, 2) == 1 and f(3, 2) == 1
