_ = 0  # anchor
class CM:
    def __init__(self) -> None:
        self.n: int = 0
    def __enter__(self) -> int:
        return 0
    def __exit__(self, a: int, b: int, c: int) -> int:
        self.n = 5
        return 0


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c: CM = CM()
    with c:
        pass
    return c.n
