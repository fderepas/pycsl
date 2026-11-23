import rt80_cls_a


#@ ensures \result == 2
#@ assigns \nothing
def base__m(k: int) -> int:
    return 2


class X(rt80_cls_a.Base):
    pass


#@ ensures \result == 2
#@ assigns \nothing
def g(x: X) -> int:
    return x.m()

if __name__ == "__main__":
    print(g(X()))
