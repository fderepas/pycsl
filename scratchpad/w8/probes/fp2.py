class C:
    #@ requires True
    #@ ensures True
    #@ assigns self.a, self.b
    def __init__(self) -> None:
        self.a: int = 0
        self.b: int = 0

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def go(self) -> None:
        self.a = 1
        self.b = 7

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def driver() -> int:
    c = C()
    c.go()
    return c.b
