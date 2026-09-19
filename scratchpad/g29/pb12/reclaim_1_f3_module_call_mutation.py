_ = 0  # anchor


class Counter:
    #@ assigns self.n
    #@ ensures self.n == 0
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns self.n
    #@ ensures self.n == 3
    def bump(self) -> int:
        self.n = 3
        return 0


counter = Counter()
counter.bump()


#@ ensures \result == 1
#@ fresh_globals
def probe() -> int:
    return counter.n
