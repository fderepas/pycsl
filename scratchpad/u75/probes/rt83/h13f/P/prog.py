import zv83h13f.b

class K:
    @staticmethod
    def one() -> int:
        return 2


def _sw() -> None:
    zv83h13f.__dict__["b"] = K


_sw()


#@ ensures \result == 1
def g() -> int:
    return zv83h13f.b.one()


print("result", g())
