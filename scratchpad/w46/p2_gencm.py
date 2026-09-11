# probe: @contextmanager generator CM — the half route #38 left unrefused
from contextlib import contextmanager
_ = 0  # anchor

class G:
    def __init__(self) -> None:
        self.v: int = 0


g = G()


@contextmanager
def cm():
    g.v = 1
    yield
    g.v = 5


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    with cm():
        pass
    return g.v
