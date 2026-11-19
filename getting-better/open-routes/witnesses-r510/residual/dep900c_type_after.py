class C:
    def __init__(self, v: int) -> None:
        self.v = v

    #@ ensures \result == self.v
    def get(self) -> int:
        return self.v


type C = int
