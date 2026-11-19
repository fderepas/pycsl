_ = 0  # anchor


class Alpha:
    def __init__(self) -> None:
        self.k = 1

    #@ ensures \result == 1
    def get(self) -> int:
        return 1


class Beta:
    def __init__(self) -> None:
        self.k = 2

    #@ ensures \result == 1
    def get(self) -> int:
        return 2


#@ ensures \result == 1
def probe(flag: int) -> int:
    o = Beta() if flag > 0 else Alpha()
    return o.get()
