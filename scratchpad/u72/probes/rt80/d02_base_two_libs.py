import rt80_cls_a
import rt80_cls_b


class X(rt80_cls_a.Base):
    pass


class Y(rt80_cls_b.Base):
    pass


#@ ensures \result == 11 or \result == 22
#@ assigns \nothing
def g() -> int:
    return X().m() + 10 * Y().m()

if __name__ == "__main__":
    print(g())
