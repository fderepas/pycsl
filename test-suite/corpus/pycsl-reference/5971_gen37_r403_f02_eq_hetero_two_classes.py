r"""Test 5971 -- gen #37 route #403 (expected FAIL): red team 32 witness `f02_eq_hetero_two_classes` -- a verified `__eq__` annotated `other: "A"` is compared with a value of another class (PROVED at base 4431ef86f; CPython violates, see the driver). REFUSED (PYCSL-R402-UNVERIFIED-EQ: only `def __eq__(self, o: object)` counts as verified, route #403).
"""
# pycsl-expected: FAIL
class A:
    def __init__(self, x: int) -> None:
        self.x: int = x

    #@ no_exception \all
    def __hash__(self) -> int:
        return 0

    #@ no_exception \all
    def __eq__(self, other: "A") -> bool:
        return self.x == other.x


class B:
    def __init__(self) -> None:
        self.y: int = 0

    #@ no_exception \all
    def __hash__(self) -> int:
        return 0


#@ no_exception \all
def f(a: A, b: B) -> int:
    s = {a, b}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(A(1), B())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
