r"""Test 9598 -- route #590 WITNESS (expected FAIL: REFUSED PYCSL-R590-RAISE-NON-EXCEPTION at HEAD, every model): the class chain `E(B)`, `B` a plain class, never reaches BaseException; raised bare (`raise E`) under `except E`. CPython raises TypeError.
"""
# pycsl-expected: FAIL
class B:
    pass


class E(B):
    pass


#@ no_exception \all
#@ ensures \result == 1
def f(k: int) -> int:
    try:
        raise E
    except E:
        return 1
    return 0


if __name__ == "__main__":
    try:
        print(f(0))
    except Exception as e:
        print("VIOLATION", type(e).__name__)
