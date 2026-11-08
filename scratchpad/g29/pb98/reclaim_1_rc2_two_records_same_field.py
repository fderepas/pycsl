_ = 0  # anchor


class A:
    def __init__(self) -> None:
        self.v = 1


class B:
    def __init__(self) -> None:
        self.v = 2


#@ ensures \result == 1
def probe() -> int:
    b = B()
    return b.v
