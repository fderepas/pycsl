from rt80_cls_b import Base
import rt80_cls_a


class X(rt80_cls_a.Base):
    pass


#@ ensures \result == 2
#@ assigns \nothing
def g(x: X) -> int:
    return x.m()

if __name__ == "__main__":
    print(g(X()))
