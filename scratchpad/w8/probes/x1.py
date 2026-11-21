@mutable_state
class C:
    #@ \trusted reviewer: probe
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self) -> None:
        pass

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def go(self) -> None:
        self.b = 7

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def driver() -> int:
    c = C()
    c.go()
    return c.b
