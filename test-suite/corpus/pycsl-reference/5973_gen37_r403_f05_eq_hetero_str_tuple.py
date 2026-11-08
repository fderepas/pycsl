r"""Test 5973 -- gen #37 route #403 (expected FAIL): red team 32 witness `f05_eq_hetero_str_tuple` -- a verified `__eq__` annotated `other: "A"` is compared with a value of another class (PROVED at base 4431ef86f; CPython violates, see the driver). REFUSED (PYCSL-R402-UNVERIFIED-EQ: only `def __eq__(self, o: object)` counts as verified, route #403).
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


#@ no_exception \all
def f(a: A) -> int:
    s = {(a, 1), (0, 1)}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(A(1))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
