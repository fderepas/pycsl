#@ ensures \result == 1
#@ assigns \nothing
def helper() -> int:
    return 1

class C:
    def __init__(self) -> None:
        self.v = 0

    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return helper()
