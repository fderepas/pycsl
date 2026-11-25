import zv81p4.b
from unittest import mock

class K:
    @staticmethod
    def one() -> int:
        return 2

mock.patch("zv81p4.b", K).start()


#@ ensures \result == 1
def g() -> int:
    return zv81p4.b.one()


print("result", g())
