class Ab:
    def __init__(self) -> None:
        self.v = 1

    #@ ensures \result == 1
    #@ assigns \nothing
    def m1(self) -> int:
        return 1


class AB:
    def __init__(self) -> None:
        self.w = 2

    #@ ensures \result == 2
    #@ assigns \nothing
    def m2(self) -> int:
        return 2


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    a = Ab()
    return a.m1()
