import importlib
import zv7d4


def h() -> None:
    importlib.import_module("zv7d4.b")


#@ ensures \result == 1
def g() -> int:
    return zv7d4.b()


h()
print("result", g())
