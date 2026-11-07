class C:
    #@ requires True
    #@ assigns self.x
    #@ ensures self.x == 99
    def __init__(self) -> None:
        self.x: int = 7

#@ requires True
#@ ensures \result == 99
#@ assigns \nothing
def driver() -> int:
    c = C()
    return c.x
