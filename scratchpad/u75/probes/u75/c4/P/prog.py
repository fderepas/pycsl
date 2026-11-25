import sys
import zv75c4.b
import zv75c4.k


#@ ensures \result == 1
def g() -> int:
    return zv75c4.b.one()


print(zv75c4.k.CONST, len(sys.argv) > 0, sys.argv[0] != "")
if zv75c4.b is not None:
    print("result", g())
