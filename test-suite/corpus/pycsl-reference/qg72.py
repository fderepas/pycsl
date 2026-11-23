# u72 helper (routes #629 / #630, review rt80 R2 / R3a): a library class `Base` whose `m` returns 1.


class Base:
    def __init__(self) -> None:
        self.v = 0

    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1
