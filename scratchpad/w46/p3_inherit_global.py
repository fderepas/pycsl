# probe: route #38 bypass via INHERITED __enter__/__exit__, mutating a global
_ = 0  # anchor

class G:
    def __init__(self) -> None:
        self.v: int = 0


g = G()


class Base:
    def __enter__(self) -> int:
        return 0
    def __exit__(self, a: int, b: int, c: int) -> int:
        g.v = 5
        return 0


class CM(Base):
    def __init__(self) -> None:
        self.d: int = 0


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = CM()
    with c:
        pass
    return g.v
