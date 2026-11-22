import zt781.b


#@ ensures \result == 1
def g() -> int:
    return zt781.b.one()


print("result", g())
