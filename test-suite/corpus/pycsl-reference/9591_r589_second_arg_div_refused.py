r"""Test 9591 -- route #589 WITNESS (expected FAIL: REFUSED PYCSL-R589-RAISE-ARGUMENT-UNEVALUATED at HEAD, every model; PROVED at base, rt56 ha1759): `raise E("a", 1 // k)`, the dropped second argument raises ZeroDivisionError at k == 0. CPython: ZeroDivisionError.
"""
# pycsl-expected: FAIL
class E(Exception):
    pass


#@ no_exception \all
#@ ensures \result == 1
def f(k: int) -> int:
    try:
        raise E("a", 1 // k)
    except E:
        return 1
    return 0


if __name__ == "__main__":
    try:
        print(f(0))
    except Exception as e:
        print("VIOLATION", type(e).__name__)
