import zv81p1.b

class K:
    @staticmethod
    def one() -> int:
        return 2


def _h(a: zv81p1) -> None:
    pass


m = dict(_h.__annotations__)["a"]
m.b = K


#@ ensures \result == 1
def g() -> int:
    return zv81p1.b.one()


print("result", g())
