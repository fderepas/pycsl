import zv83k1.b
from unittest.mock import patch


class K:
    @staticmethod
    def one() -> int:
        return 2


patch("zv83k1.b", K).start()


#@ ensures \result == 1
def g() -> int:
    return zv83k1.b.one()


print("result", g())
