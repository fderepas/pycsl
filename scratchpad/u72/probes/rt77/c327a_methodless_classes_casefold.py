class Ab:
    x: int = 1


class AB:
    x: int = 2


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return 1
