import zt784.b


#@ ensures \result == 1
def g() -> int:
    return zt784.b.one()


print("result", g())
