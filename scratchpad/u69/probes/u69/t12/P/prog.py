import zu694.b
import zu694.d


#@ ensures \result == 1
def g() -> int:
    zu694.d.swap()
    return zu694.b.one()


print("result", g())
