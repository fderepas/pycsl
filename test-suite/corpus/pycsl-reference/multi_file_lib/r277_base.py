class A:
    def __init__(self) -> None:
        self.v: int = 0
    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1

#@ ensures \result == 1
#@ assigns \nothing
def use(a: A) -> int:
    return a.m()
