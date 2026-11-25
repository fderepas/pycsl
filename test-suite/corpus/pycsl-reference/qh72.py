# u72 helper (route #629, review rt80 R2): a second library class also named `Base`, whose `m` returns 2.


class Base:
    def __init__(self) -> None:
        self.v = 0

    #@ ensures \result == 2
    #@ assigns \nothing
    def m(self) -> int:
        return 2
