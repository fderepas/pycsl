r"""Test 5788 -- gen #37 route #402 (expected FAIL): a plain base `B` hashed as `{a, b}` while `__main__` passes instances of the file subclass `D(B)` with a raising `__eq__` (CPython ValueError; PROVED at base 526d534de). REFUSED (PYCSL-R402-UNVERIFIED-EQ: closed-world subclass closure).
"""
# pycsl-expected: FAIL
class B:
    def __init__(self) -> None:
        self.x: int = 1


class D(B):
    #@ no_exception \all
    def __hash__(self) -> int:
        return 0

    def __eq__(self, o: object) -> bool:
        if self.x == 1:
            raise ValueError("e")
        return False


#@ no_exception \all
def f(a: B, b: B) -> int:
    s = {a, b}
    return 1


if __name__ == "__main__":
    try:
        print("result", f(D(), D()))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
