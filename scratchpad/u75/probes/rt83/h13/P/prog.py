import zv83h13.b

class K:
    @staticmethod
    def one() -> int:
        return 2


zv83h13.__dict__["b"] = K


#@ ensures \result == 1
def g() -> int:
    return zv83h13.b.one()


print("result", g())
