_ = 0  # anchor
class C:
    #@ class invariant self.v == 99
    #@ requires True
    #@ ensures True
    #@ assigns self.v
    def __init__(self) -> None:
        self.v: int = 0
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def g(self) -> int:
        return self.v
