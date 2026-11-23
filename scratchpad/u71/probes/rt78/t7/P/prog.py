import zt787.b


#@ ensures \result == 1
def g() -> int:
    return zt787.b.one()


print("result", g())
