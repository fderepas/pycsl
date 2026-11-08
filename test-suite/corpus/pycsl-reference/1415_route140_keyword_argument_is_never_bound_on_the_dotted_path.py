r"""Test 1415 — ROUTE #140, second shape: keyword arguments are never bound on the dotted-call path either. `c.f(k=-5)` left `args` empty, the condition again read the caller\x27s `k`, and `no_exception ValueError` PROVED while CPython raises ValueError.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class H:
    tag: int

    def __init__(self) -> None:
        self.tag = 0

    #@ raises ValueError when k < 0
    #@ assigns \nothing
    def f(self, k: int = -1) -> int:
        m = k
        if m < 0:
            raise ValueError
        return m


#@ requires k >= 0
#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    c = H()
    return c.f(k=-5)