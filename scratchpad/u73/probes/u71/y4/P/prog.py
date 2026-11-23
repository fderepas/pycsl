import zuy4.b
import zuy4.d


#@ ensures \result == 1
def g() -> int:
    zuy4.d.swap()
    return zuy4.b.one()


print("result", g())
