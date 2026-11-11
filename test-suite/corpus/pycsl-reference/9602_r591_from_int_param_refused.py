r"""Test 9602 -- route #591 WITNESS (expected FAIL: REFUSED PYCSL-R591-RAISE-FROM-NON-EXCEPTION at HEAD, every model; PROVED at base, rt56 ha1787): `raise E("a") from k` with an `int` parameter. CPython raises TypeError.
"""
# pycsl-expected: FAIL
class E(Exception):
    pass


#@ no_exception \all
#@ ensures \result == 1
def f(k: int) -> int:
    try:
        raise E("a") from k
    except E:
        return 1
    return 0


if __name__ == "__main__":
    try:
        print(f(0))
    except Exception as e:
        print("VIOLATION", type(e).__name__)
