from zq76 import b


#@ ensures \result == 2
def g() -> int:
    return b.one()


print("result", g())
