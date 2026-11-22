import zu695.b


#@ ensures \result == 1
def g() -> int:
    return zu695.b.one()


print("result", g())
