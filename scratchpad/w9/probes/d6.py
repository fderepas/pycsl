_ = 0  # anchor
class C:
    #@ requires True
    #@ ensures self.v == 1
    #@ assigns self.v
    def __init__(self) -> None:
        self.v: int = 1
    @property
    #@ requires True
    #@ ensures \result == 99
    #@ assigns \nothing
    def p(self) -> int:
        return self.v
    #@ requires self.v == 1
    #@ ensures \result == 99
    #@ assigns \nothing
    def g(self) -> int:
        return self.p
