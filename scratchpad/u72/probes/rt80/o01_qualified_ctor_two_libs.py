import rt80_cls_a
import rt80_cls_b


#@ ensures \result == 11
#@ assigns \nothing
def g() -> int:
    x = rt80_cls_a.Base()
    y = rt80_cls_b.Base()
    return x.m() + 10 * y.m()

if __name__ == "__main__":
    print(g())
