class C:
    #@ invariant True
    def __init__(self) -> None:
        self.v: float = 0.1

    #@ ensures \result == 0.3
    #@ assigns \nothing
    def g(self) -> float:
        return self.v + 0.2
