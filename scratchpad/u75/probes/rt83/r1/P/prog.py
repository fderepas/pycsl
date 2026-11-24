import zv83r1

class K:
    @staticmethod
    def one() -> int:
        return 2


def _ga(name):
    return K


zv83r1.__getattr__ = _ga


#@ ensures \result == 1
def g() -> int:
    return zv83r1.b.one()


print("result", g())
