r"""Test 9597 -- route #590 WITNESS (expected FAIL: REFUSED PYCSL-R590-RAISE-NON-EXCEPTION at HEAD, every model; PROVED at base, rt56 ha1781): a plain class with an `__init__` raised and caught by its own name. CPython raises TypeError.
"""
# pycsl-expected: FAIL
class E:
    def __init__(self, m: str) -> None:
        self.m = m


#@ no_exception \all
#@ ensures \result == 1
def f(k: int) -> int:
    try:
        raise E("a")
    except E:
        return 1
    return 0


if __name__ == "__main__":
    try:
        print(f(0))
    except Exception as e:
        print("VIOLATION", type(e).__name__)
