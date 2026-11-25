from zv83g1 import b


#@ ensures \result == 1
def g() -> int:
    return b.one()


print("result", g())
