#@ class invariant self.v > 0
class C:
    #@ requires True
    #@ ensures True
    #@ assigns self.v
    def __init__(self) -> None:
        self.v: int = 0

#@ requires True
#@ ensures \result > 0
#@ assigns \nothing
def driver() -> int:
    c = C()
    return c.v
