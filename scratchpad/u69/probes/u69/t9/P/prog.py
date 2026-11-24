import zu691.b
import zu691.c
import zu691 as _p
_p.b = _p.c


#@ ensures \result == 1
def g() -> int:
    return zu691.b.one()


print("result", g())
