"""G29 route #143 helper — a CLASS method whose raises condition names this module's constant."""
LIM = -1


class K:
    kf: int

    def __init__(self, kf: int) -> None:
        self.kf = kf

    #@ raises ValueError when LIM < 0
    #@ assigns \nothing
    def m(self, k: int) -> int:
        if LIM < 0:
            raise ValueError
        return k
