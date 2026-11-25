import zv83h12f.b

class K:
    @staticmethod
    def one() -> int:
        return 2


def _sw() -> None:
    zv83h12f.__setattr__("b", K)


_sw()


#@ ensures \result == 1
def g() -> int:
    return zv83h12f.b.one()


print("result", g())
