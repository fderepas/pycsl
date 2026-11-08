r"""Test 5801 -- gen #37 route #402 (expected PASS): CONTROL: an unverified raising `__eq__` with a verified `__hash__` is never called by a one-element set display, or a one-element display of a tuple holding it (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
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
#@ ensures \result == 1
def f(d: D) -> int:
    s = {d}
    t = {(d, 1)}
    return 1


if __name__ == "__main__":
    print(f(D()))
