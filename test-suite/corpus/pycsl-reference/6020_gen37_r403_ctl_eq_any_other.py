r"""Test 6020 -- gen #37 route #403 (expected PASS): CONTROL: `__eq__(self, other: object)` verified `no_exception \all`, compared with an `int`, a `bool` and inside a tuple (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
class A:
    def __init__(self, x: int) -> None:
        self.x: int = x

    #@ no_exception \all
    def __hash__(self) -> int:
        return self.x

    #@ no_exception \all
    def __eq__(self, other: object) -> bool:
        return False


#@ no_exception \all
#@ ensures \result == 1
def f(a: A, b: A) -> int:
    s = {a, 1}
    t = {a, b, False}
    u = {(a, 1), (0, 1)}
    return 1


if __name__ == "__main__":
    print(f(A(1), A(2)))
