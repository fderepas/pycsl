_ = 0  # anchor


class My_box:
    def __init__(self) -> None:
        self.n = 1

    #@ ensures \result == -1
    def get(self) -> int:
        return 1


class MY_BOX:
    def __init__(self) -> None:
        self.n = 2

    #@ ensures \result == -1
    def get(self) -> int:
        return 2


#@ ensures \result == -1
def probe() -> int:
    o = MY_BOX()
    return o.get()
