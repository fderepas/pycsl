class C:
    #@ requires True
    #@ ensures \length(self.d) == 4
    #@ assigns self.d
    def __init__(self) -> None:
        self.d: list = bytearray(4)

    #@ requires 0 <= i and i < 4
    #@ ensures True
    #@ assigns \nothing
    def poke(self, i: int) -> None:
        self.d[i] = 7

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def driver() -> int:
    c = C()
    c.poke(0)
    return c.d[0]
