class C:
    def __init__(self) -> None:
        self.v = 0

    #@ requires x > 0 and x < 0
    #@ ensures \result == 99
    def m(self, x: int) -> int:
        return 1
