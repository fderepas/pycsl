r"""Test 5300 -- gen #37 route #387 (expected FAIL): `global get` in a class body before `def get`: the def binds a module global, `c.get()` raises AttributeError; PROVED at base. REFUSED (class-body global naming a member, route #387).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.n: int = 0

    global get
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
