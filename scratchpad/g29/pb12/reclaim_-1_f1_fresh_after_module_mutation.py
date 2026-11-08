_ = 0  # anchor


class Counter:
    #@ assigns self.n
    #@ ensures self.n == 0
    def __init__(self) -> None:
        self.n: int = 0


counter = Counter()
counter.n = 7


#@ ensures \result == -1
#@ fresh_globals
def probe() -> int:
    #@ assert counter.n == 0
    return counter.n
