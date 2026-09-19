_ = 0  # anchor


class C:
    count: int = 0

    def __init__(self) -> None:
        self.n = 0

    #@ ensures \result == 0
    def bump(self) -> int:
        C.count = C.count + 1
        return C.count


def probe() -> int:
    c = C()
    c.bump()
    return c.bump()
