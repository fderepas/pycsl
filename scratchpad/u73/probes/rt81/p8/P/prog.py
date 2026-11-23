import zv81p8.b


def _sw() -> None:
    class C(zv81p8):
        pass


_sw()


#@ ensures \result == 1
def g() -> int:
    return zv81p8.b.one()


print("result", g())
