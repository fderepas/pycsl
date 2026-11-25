import rt80_cls_a
from rt80_cls_a import Base


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    b = rt80_cls_a.Base()
    return b.m()

if __name__ == "__main__":
    print(g())
