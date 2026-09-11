_ = 0  # anchor
class C:
    def __init__(self) -> None:
        self._v: int = 0

    @property
    def v(self) -> int:
        return 7


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.v
