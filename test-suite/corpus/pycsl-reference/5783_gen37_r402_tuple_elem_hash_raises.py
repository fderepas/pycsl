r"""Test 5783 -- gen #37 route #402 (expected FAIL): a tuple `(d, 1)` in a set hashes its element `d`, whose own `__hash__` raises ValueError (CPython ValueError; PROVED at base 526d534de). REFUSED (PYCSL-R349-UNHASHABLE-RECORD).
"""
# pycsl-expected: FAIL
class D:
    def __init__(self) -> None:
        self.x: int = 1

    def __hash__(self) -> int:
        if self.x == 1:
            raise ValueError("h")
        return 0


#@ no_exception \all
def f(a: D, b: D) -> int:
    s = {(a, 1)}
    return 1


if __name__ == "__main__":
    try:
        print("result", f(D(), D()))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
