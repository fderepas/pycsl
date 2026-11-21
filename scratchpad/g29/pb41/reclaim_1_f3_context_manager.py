_ = 0  # anchor


class Ctx:
    def __init__(self) -> None:
        self.n = 0

    def __enter__(self) -> int:
        return 1

    def __exit__(self, a: int, b: int, c: int) -> int:
        return 0


#@ ensures \result == 1
def probe() -> int:
    c = Ctx()
    with c as v:
        return v + 4
