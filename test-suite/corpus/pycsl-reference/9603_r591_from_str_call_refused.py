r"""Test 9603 -- route #591 WITNESS (expected FAIL: REFUSED PYCSL-R591-RAISE-FROM-NON-EXCEPTION at HEAD, every model): `raise E("a") from str(k)`, a pure builtin call route #310 admits, builds a string cause. CPython raises TypeError.
"""
# pycsl-expected: FAIL
class E(Exception):
    pass


#@ no_exception \all
#@ ensures \result == 1
def f(k: int) -> int:
    try:
        raise E("a") from str(k)
    except E:
        return 1
    return 0


if __name__ == "__main__":
    try:
        print(f(0))
    except Exception as e:
        print("VIOLATION", type(e).__name__)
