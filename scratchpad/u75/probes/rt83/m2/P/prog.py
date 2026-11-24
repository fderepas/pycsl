import zv83m2.b

class K:
    @staticmethod
    def one() -> int:
        return 2


object.__setattr__(zv83m2, "b", K)


#@ ensures \result == 1
def g() -> int:
    return zv83m2.b.one()


print("result", g())
