from zu698 import d0


#@ ensures \result == 1
def g() -> int:
    return d0.get()


print("result", g())
