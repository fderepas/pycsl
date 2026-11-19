_ = 0  # anchor
class Base:
    def __enter__(self) -> int:
        return 0
    def __exit__(self, a: int, b: int, c: int) -> int:
        self.n = 5
        return 0


class CM(Base):
    def __init__(self) -> None:
        self.n: int = 0


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = CM()
    with c:
        pass
    return c.n
