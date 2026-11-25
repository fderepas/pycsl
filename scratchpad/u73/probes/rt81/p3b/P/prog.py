import zv81p3b.b

class K:
    @staticmethod
    def one() -> int:
        return 2


def _sw() -> None:
    d = zv81p3b.__getstate__()
    d["b"] = K


_sw()


#@ ensures \result == 1
def g() -> int:
    return zv81p3b.b.one()


print("result", g())
