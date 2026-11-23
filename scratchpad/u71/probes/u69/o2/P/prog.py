from zu696 import b


#@ ensures \result == 1
def g() -> int:
    return b()


print("result", g())
