from zk76.dep import f


#@ ensures \result == 1
def g() -> int:
    return f()


print("result", g())
