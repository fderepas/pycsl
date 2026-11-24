import zuy3.b
import zuy3.d


#@ ensures \result == 1
def g() -> int:
    zuy3.d.swap(zuy3)
    return zuy3.b.one()


print("result", g())
