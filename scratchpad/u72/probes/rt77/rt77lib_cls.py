class C:
    def __init__(self) -> None:
        self.v = 0

    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self, x: int) -> int:
        return 1
