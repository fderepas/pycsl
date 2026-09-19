_ = 0  # anchor


class Inner:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires self.x != 0
    #@ ensures \result == 1
    def get(self) -> int:
        return self.x // self.x


#@ ensures \result == 1
def probe() -> int:
    o = Inner(3)
    o.get()
    return 5
