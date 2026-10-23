from typing import Optional


class R:
    def __init__(self, n):
        self.n: int = n


#@ no_exception AttributeError
#@ ensures \result == 0
def probe() -> int:
    x: Optional[R] = None
    return x.n
