import zv83k2.b
from unittest import mock


class K:
    @staticmethod
    def one() -> int:
        return 2


mock.patch.object(zv83k2, "b", K).start()


#@ ensures \result == 1
def g() -> int:
    return zv83k2.b.one()


print("result", g())
