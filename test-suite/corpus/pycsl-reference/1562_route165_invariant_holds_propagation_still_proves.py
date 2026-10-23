r"""Test 1562 - ROUTE #165 control (gen #29): with no outside store the invariant holds and `c.get() >= 0` PROVES on both sides.
"""
_ = 0  # anchor


#@ class invariant self.x >= 0
class C:
    def __init__(self) -> None:
        self.x = 1

    #@ ensures \result >= 0
    def get(self) -> int:
        return self.x


#@ ensures \result >= 0
def probe() -> int:
    c = C()
    return c.get()

