import zk88
from dep88 import g


#@ ensures \result == 1
def h() -> int:
    return zk88.f() + g() - 1


print("result", h())
