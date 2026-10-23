r"""Test 1563 - ROUTE #165 control (gen #29): an outside store that keeps the invariant (`c.x = 7`) still PROVES `c.get() >= 0` on both sides.
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
    c.x = 7
    return c.get()
