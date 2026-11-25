import zt785.b


#@ ensures \result == 1
def g() -> int:
    return zt785.b.one()


print("result", g())
