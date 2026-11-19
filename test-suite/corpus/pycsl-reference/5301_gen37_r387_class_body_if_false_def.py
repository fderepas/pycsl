r"""Test 5301 -- gen #37 route #387 (expected FAIL): `def get` under `if False:` in a class body; PROVED at base (CPython AttributeError). REFUSED (member under a compound statement, route #387).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.n: int = 0

    if False:
        #@ ensures \result == 1
        #@ assigns \nothing
        def get(self) -> int:
            return 1


#@ ensures \result == 1
def f(c: C) -> int:
    return c.get()


if __name__ == "__main__":
    try:
        r = f(C())
        print("VIOLATION f =", r) if r != 1 else print("no violation")
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
