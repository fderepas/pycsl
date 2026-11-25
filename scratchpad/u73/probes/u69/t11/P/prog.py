import zu693.b


#@ ensures \result == 1
def g() -> int:
    return zu693.b.one()


print("result", g())
