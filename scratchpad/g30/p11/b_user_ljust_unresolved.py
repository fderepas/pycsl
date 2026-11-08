class D:
    def __init__(self):
        self.n: int = 3

    #@ requires True
    #@ ensures \result == 3
    def ljust(self) -> int:
        return 3


#@ ensures \result == 3
def probe() -> int:
    d = D()
    return d.ljust()
