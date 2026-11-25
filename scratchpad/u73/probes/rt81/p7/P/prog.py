import zv81p7.b


class K:
    @staticmethod
    def one() -> int:
        return 2


def _sw() -> None:
    m = zv81p7.__loader__.load_module("zv81p7")
    m.b = K


_sw()


#@ ensures \result == 1
def g() -> int:
    return zv81p7.b.one()


print("result", g())
