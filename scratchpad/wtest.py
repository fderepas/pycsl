def mutable_state(cls):
    return cls


#@ class invariant 0 <= self.pos
@mutable_state
class C:
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self, n: int) -> None:
        self.pos: int = 0

    #@ \trusted reviewer: t
    #@ requires True
    #@ ensures True
    #@ assigns self.pos
    def bump(self) -> int:
        return 0

    #@ requires True
    #@ ensures self.pos == \old(self.pos)
    #@ assigns self.pos
    def caller(self) -> int:
        x = self.bump()
        return x
