class C:
    def __init__(self) -> None:
        self.k = 0

    def go(self, v: int) -> int:
        if v < 0:
            raise ValueError()
        return v


def fgo(v: int) -> int:
    if v < 0:
        raise ValueError()
    return v
