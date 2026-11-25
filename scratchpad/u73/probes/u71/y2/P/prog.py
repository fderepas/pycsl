import zuy2.b
import zuy2.d


#@ ensures \result == 1
def g() -> int:
    zuy2.d.swap()
    return zuy2.b.one()


print("result", g())
