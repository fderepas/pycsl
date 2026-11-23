import rt80_cls_h


#@ ensures \result == 2
#@ assigns \nothing
def helper() -> int:
    return 2


class X(rt80_cls_h.C):
    pass


obj = X()


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return obj.m()

if __name__ == "__main__":
    print(g())
