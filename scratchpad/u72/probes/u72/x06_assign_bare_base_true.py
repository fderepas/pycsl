import rt80_cls_b

Base = rt80_cls_b.Base


class X(Base):
    pass


#@ ensures \result == 2
#@ assigns \nothing
def g(x: X) -> int:
    return x.m()

if __name__ == "__main__":
    print(g(X()))
