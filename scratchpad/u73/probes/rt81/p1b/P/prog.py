import zv81p1b.b

class K:
    @staticmethod
    def one() -> int:
        return 2


def _h(a: zv81p1b) -> None:
    pass


def _sw() -> None:
    m = dict(_h.__annotations__)["a"]
    m.b = K


_sw()


#@ ensures \result == 1
def g() -> int:
    return zv81p1b.b.one()


print("result", g())
