import zuy5.b
import zuy5.d


#@ ensures \result == 1
def g() -> int:
    zuy5.d.swap()
    return zuy5.b.one()


print("result", g())
