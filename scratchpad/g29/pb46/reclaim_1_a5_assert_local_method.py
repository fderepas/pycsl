_ = 0  # anchor


class Box:
    def __init__(self) -> None:
        self.n = 0

    #@ assigns self.n
    #@ ensures self.n == 5
    def setit(self) -> int:
        self.n = 5
        return 1


#@ ensures \result == 1
def probe() -> int:
    b = Box()
    assert b.setit() == 1
    return b.n
