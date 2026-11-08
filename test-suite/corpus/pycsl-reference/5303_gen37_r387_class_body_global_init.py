r"""Test 5303 -- gen #37 route #387 (expected FAIL): `global __init__` in a class body: `C()` runs `object.__init__`, `self.n` is never set, `get()` under `no_exception \all` raises AttributeError; PROVED at base. REFUSED (route #387).
"""
# pycsl-expected: FAIL
#@ class invariant self.n >= 0
class C:
    global __init__

    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result >= 0
    #@ no_exception \all
    def get(self) -> int:
        return self.n


if __name__ == "__main__":
    try:
        r = C().get()
        print("no violation", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
