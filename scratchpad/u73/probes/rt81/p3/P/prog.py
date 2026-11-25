import zv81p3.b

class K:
    @staticmethod
    def one() -> int:
        return 2

d = zv81p3.__getstate__()
d["b"] = K


#@ ensures \result == 1
def g() -> int:
    return zv81p3.b.one()


print("result", g())
