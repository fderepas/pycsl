r"""Test 1663 - ROUTE #187 control (gen #29): a `#@ fresh_globals` driver over a module body that is only a docstring, a class definition and the single global binding still proves. The driver reads the global's constructor post-state and computes with it, so the contract is not discharged by a literal return.
"""
_ = 0  # anchor


class Gauge:
    #@ assigns self.n
    #@ ensures self.n == 4
    def __init__(self) -> None:
        self.n: int = 4


gauge = Gauge()


#@ ensures \result == 9
#@ fresh_globals
def probe() -> int:
    #@ assert gauge.n == 4
    return gauge.n * 2 + 1
