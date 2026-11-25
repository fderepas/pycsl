import zv83t5.b
from test.support import swap_attr

class K:
    @staticmethod
    def one() -> int:
        return 2


def _sw() -> None:
    global _cm
    _cm = swap_attr(zv83t5, "b", K)
    _cm.__enter__()


_sw()


#@ ensures \result == 1
def g() -> int:
    return zv83t5.b.one()


print("result", g())
