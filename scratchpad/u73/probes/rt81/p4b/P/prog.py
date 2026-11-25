import zv81p4b.b

class K:
    @staticmethod
    def one() -> int:
        return 2


def _sw() -> None:
    import unittest.mock
    unittest.mock.patch("zv81p4b.b", K).start()


_sw()


#@ ensures \result == 1
def g() -> int:
    return zv81p4b.b.one()


print("result", g())
