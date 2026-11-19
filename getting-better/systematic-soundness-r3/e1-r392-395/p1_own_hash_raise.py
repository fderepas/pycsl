class D:
    def __init__(self) -> None:
        self.x: int = 1

    def __hash__(self) -> int:
        if self.x == 1:
            raise ValueError("h")
        return 0


#@ no_exception \all
def f(d: D) -> int:
    s = {d}
    return len(s)
