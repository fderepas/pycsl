_ = 0  # anchor


class Inner:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires self.x != 0
    #@ ensures \result == 1
    def get(self) -> int:
        return self.x // self.x


_g = Inner(0)


#@ ensures \result == 5
def probe() -> int:
    _g.get()
    return 5
