class C:
    def __init__(self):
        self.n: int = 7

    #@ requires True
    #@ ensures \result == 7
    def encode(self) -> int:
        return 7


#@ ensures \result == 7
def probe() -> int:
    c = C()
    return c.encode()
