import rt80_cls_a
import rt80_cls_b


class X(rt80_cls_a.Base):
    pass


class Y(rt80_cls_b.Base):
    pass


#@ ensures \result == 21
#@ assigns \nothing
def g(x: X, y: Y) -> int:
    return x.m() + 10 * y.m()

if __name__ == "__main__":
    print(g(X(), Y()))
