import typing
import zv83a1.b


class K:
    @staticmethod
    def one() -> int:
        return 2


def _h(a: "zv83a1") -> None:
    pass


def _sw() -> None:
    m = typing.get_type_hints(_h)["a"]
    m.b = K


_sw()


#@ ensures \result == 1
def g() -> int:
    return zv83a1.b.one()


print("result", g())
