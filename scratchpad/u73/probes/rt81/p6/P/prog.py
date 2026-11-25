import zv81p6.b

class K:
    @staticmethod
    def one() -> int:
        return 2


class H:
    a: zv81p6


m = dict(H.__annotations__)["a"]
m.b = K


#@ ensures \result == 1
def g() -> int:
    return zv81p6.b.one()


print("result", g())
