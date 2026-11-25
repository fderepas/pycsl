import zv75c7.b
import zv75c7.k


#@ ensures \result == 1
def g() -> int:
    return zv75c7.b.one()


print(isinstance(zv75c7.k.Base(), zv75c7.k.Base))
print("result", g())
