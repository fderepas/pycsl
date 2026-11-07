r"""Test 5785 -- gen #37 route #402 (expected FAIL): a verified `__hash__` returning 0 and an `__eq__` that raises; `{a, b}` compares the two on the hash collision (CPython ValueError; PROVED at base 526d534de). REFUSED (PYCSL-R402-UNVERIFIED-EQ).
"""
# pycsl-expected: FAIL
class D:
    def __init__(self) -> None:
        self.x: int = 1

    #@ no_exception \all
    def __hash__(self) -> int:
        return 0

    def __eq__(self, o: object) -> bool:
        if self.x == 1:
            raise ValueError("e")
        return False


#@ no_exception \all
def f(a: D, b: D) -> int:
    s = {a, b}
    return 1


if __name__ == "__main__":
    try:
        print("result", f(D(), D()))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
