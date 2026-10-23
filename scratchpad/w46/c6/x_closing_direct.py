_ = 0  # anchor
g_n = 0


class closing:
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
    with closing():
        pass
    return 0
