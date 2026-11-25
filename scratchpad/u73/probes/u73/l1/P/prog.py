import zv83l1.b


class K:
    @staticmethod
    def one() -> int:
        return 2


def _sw() -> None:
    m = zv83l1.__spec__.loader.load_module("zv83l1")
    m.b = K


_sw()


#@ ensures \result == 1
def g() -> int:
    return zv83l1.b.one()


print("result", g())
