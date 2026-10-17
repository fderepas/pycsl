class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 0
    #@ assigns \nothing
    #@ \diverges
    #@ no_exception \all
    def m(self, k: int) -> int:
        return self.m(k)
