_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n = 1

    def __getattr__(self, name: str) -> int:
        return 42


#@ ensures \result == 0
def probe() -> int:
    c = C()
    return c.missing
