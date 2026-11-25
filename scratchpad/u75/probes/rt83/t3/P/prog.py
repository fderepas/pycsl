import zv83t3.b
from _pytest.monkeypatch import MonkeyPatch

class K:
    @staticmethod
    def one() -> int:
        return 2


MonkeyPatch().setitem(zv83t3.__dict__, "b", K)


#@ ensures \result == 1
def g() -> int:
    return zv83t3.b.one()


print("result", g())
