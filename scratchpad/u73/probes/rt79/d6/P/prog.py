import importlib
import zv7d6


def h() -> None:
    __import__("zv7d6.b")


#@ ensures \result == 1
def g() -> int:
    return zv7d6.b()


h()
print("result", g())
