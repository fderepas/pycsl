_ = 0  # anchor


class C:
    LIMIT: int = 10

    def __init__(self) -> None:
        self.n = 0


#@ ensures \result == 0
def probe() -> int:
    return C.LIMIT
