class C:
    #@ requires True
    #@ ensures True
    def __init__(self) -> None:
        self.x = 1

#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    c = C()
    d = getattr(c, "missing", [])
    if d == 0:
        return 7
    return 0
