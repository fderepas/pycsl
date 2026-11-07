r"""Test 5305 -- gen #37 route #387 (expected FAIL): `def get` after `raise ValueError` inside a class-body `try:`; PROVED at base (CPython AttributeError). REFUSED (route #387).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.n: int = 0

    try:
        raise ValueError
        #@ ensures \result == 1
        #@ assigns \nothing
        def get(self) -> int:  # unreachable
            return 1
    except ValueError:
        pass


#@ ensures \result == 1
def f(c: C) -> int:
    return c.get()


if __name__ == "__main__":
    try:
        r = f(C())
        print("VIOLATION f =", r) if r != 1 else print("no violation")
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
