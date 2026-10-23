#@ ensures \result == y + 1
#@ assigns \nothing
def inc(y: int) -> int:
    return y + 1


#@ ensures \result == y - 1
#@ assigns \nothing
def dec(y: int) -> int:
    return y - 1


class K:
    def __init__(self) -> None:
        self.a = 0

    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1

    #@ ensures \result == 2
    #@ assigns \nothing
    def n(self) -> int:
        return 2
