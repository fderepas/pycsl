import zv83m3.b

class K:
    @staticmethod
    def one() -> int:
        return 2


vars(zv83m3).update(b=K)


#@ ensures \result == 1
def g() -> int:
    return zv83m3.b.one()


print("result", g())
