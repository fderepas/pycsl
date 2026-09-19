_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n = 1

    #@ ensures \result == 1
    def get(self) -> int:
        return 1


class D:
    def __init__(self) -> None:
        self.n = 2

    #@ ensures \result == 2
    def get(self) -> int:
        return 2


#@ ensures \result == 1
def probe(flag: int) -> int:
    if flag > 0:
        o = D()
    else:
        o = C()
    return o.get()
