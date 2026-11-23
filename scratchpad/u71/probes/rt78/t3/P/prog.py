import zt783.b


#@ ensures \result == 1
def g() -> int:
    return zt783.b.one()


print("result", g())
