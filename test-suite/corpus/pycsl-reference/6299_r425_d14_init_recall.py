r"""Test 6299 -- route #425 (expected FAIL): red team 33 witness `d14_init_recall` (getting-better/open-routes/witnesses-r425/d14_init_recall.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
#@ class invariant self.n >= 0
class A:
    #@ requires n >= 0
    def __init__(self, n: int) -> None:
        self.n = n

    #@ ensures \result >= 0
    #@ assigns \nothing
    def where(self) -> int:
        return self.n


#@ ensures \result >= 0
def g() -> int:
    a = A(1)
    a.__init__(-4)
    return a.where()


if __name__ == "__main__":
    try:
        r = g()
        if not (r >= 0):
            print("VIOLATION ensures", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
