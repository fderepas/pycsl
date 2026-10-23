class C:
    #@ requires True
    #@ ensures self.v == 0
    #@ assigns self.v
    def __init__(self) -> None:
        self.v: int = 0

    #@ requires True
    #@ ensures \old(self.v) == self.v
    #@ assigns self.v
    def bump(self) -> None:
        self.v = self.v + 1
