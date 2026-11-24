import zt788.b


#@ ensures \result == 1
def g() -> int:
    return zt788.b.one()


print("result", g())
