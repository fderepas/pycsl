import zv75d1.b
from hw75d1 import run

run()


#@ ensures \result == 1
def g() -> int:
    return zv75d1.b.one()


print("result", g())
