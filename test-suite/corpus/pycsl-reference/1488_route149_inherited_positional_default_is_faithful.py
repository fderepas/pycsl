r"""Test 1488 - ROUTE #149 x #147 (gen #29) positive twin of 1481: `Bee().get() == 5` PROVES (FAILS at HEAD).
"""
_ = 0  # anchor


class Ay:
    def __init__(self, r: int = 5) -> None:
        self.r = r

    #@ requires True
    #@ ensures \result == self.r
    def get(self) -> int:
        return self.r


class Bee(Ay):
    pass


#@ ensures \result == 5
#@ assigns \nothing
def probe() -> int:
    b = Bee()
    return b.get()

