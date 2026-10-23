#@ assert 1 == 2
class C:
    #@ ensures self.v == 0
    #@ assigns self.v
    def __init__(self) -> None:
        self.v: int = 0

#@ ensures \result == 0
def go() -> int:
    return 0
