import rt80_cls_a
from rt80_cls_a import Base


class X(Base):
    pass


class Y(rt80_cls_a.Base):
    pass


#@ ensures \result == 11
#@ assigns \nothing
def g(x: X, y: Y) -> int:
    return x.m() + 10 * y.m()

if __name__ == "__main__":
    print(g(X(), Y()))
