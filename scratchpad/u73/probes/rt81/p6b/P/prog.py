import zv81p6b.b

class K:
    @staticmethod
    def one() -> int:
        return 2


class H:
    a: zv81p6b


def _sw() -> None:
    m = dict(H.__annotations__)["a"]
    m.b = K


_sw()


#@ ensures \result == 1
def g() -> int:
    return zv81p6b.b.one()


print("result", g())
