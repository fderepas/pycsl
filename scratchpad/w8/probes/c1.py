class C:
    #@ requires True
    #@ assigns self.x
    #@ ensures self.x == 99
    def __init__(self) -> None:
        self.x: int = 0

    #@ requires True
    #@ assigns self.x
    #@ ensures True
    def bump(self) -> None:
        self.x = self.x + 1
