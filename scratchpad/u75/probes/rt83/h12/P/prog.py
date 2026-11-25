import zv83h12.b

class K:
    @staticmethod
    def one() -> int:
        return 2


zv83h12.__setattr__("b", K)


#@ ensures \result == 1
def g() -> int:
    return zv83h12.b.one()


print("result", g())
