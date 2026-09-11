class Counter:
    #@ requires True
    #@ ensures self.n == 0
    #@ assigns self.n
    def __init__(self) -> None:
        self.n = 0

    #@ requires True
    #@ ensures self.n == \old(self.n) + 1
    #@ assigns self.n
    def bump(self) -> None:
        self.n = self.n + 1

    #@ requires True
    #@ ensures \result == self.n
    #@ assigns \nothing
    def get(self) -> int:
        return self.n

#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = Counter()
    c.bump()
    c.bump()
    if c.get() == 2:
        return 0
    return 1
