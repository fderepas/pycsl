class Base:
    def __init__(self) -> None:
        self.v = 0

    #@ ensures \result == 2
    #@ assigns \nothing
    def m(self) -> int:
        return 2
