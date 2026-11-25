import zv83s1.b
from _pytest.monkeypatch import MonkeyPatch

class K:
    @staticmethod
    def one() -> int:
        return 2


MonkeyPatch().setattr("zv83s1.b", K)


#@ ensures \result == 1
def g() -> int:
    return zv83s1.b.one()


print("result", g())
