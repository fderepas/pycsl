r"""Test 5306 -- gen #37 route #387 (expected FAIL): `global get` at the top of a class body, caller under `no_exception \all`; PROVED at base (CPython AttributeError). REFUSED (route #387).
"""
# pycsl-expected: FAIL
class C:
    global get

    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 1
    #@ assigns \nothing
    def get(self) -> int:
        return 1


#@ ensures \result == 1
#@ no_exception \all
def f(c: C) -> int:
    return c.get()


if __name__ == "__main__":
    try:
        r = f(C())
        print("VIOLATION f =", r) if r != 1 else print("no violation")
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
