from typing import Optional


class R:
    def __init__(self, n):
        self.n: int = n


#@ ensures \result == 0
def probe() -> int:
    x: Optional[R] = None
    v = 7
    try:
        v = x.n
    except AttributeError:
        v = 7
    return v
