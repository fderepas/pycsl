class C:
    #@ requires 1 == 2
    #@ assigns self.x
    #@ ensures True
    def __init__(self) -> None:
        self.x: int = 7

#@ requires True
#@ ensures \result == 7
#@ assigns \nothing
def driver() -> int:
    c = C()
    return c.x
