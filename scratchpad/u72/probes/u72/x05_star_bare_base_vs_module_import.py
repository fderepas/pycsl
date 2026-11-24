from rt80_cls_a import *
import rt80_cls_b


class X(Base):
    pass


#@ ensures \result == 2
#@ assigns \nothing
def g(x: X) -> int:
    return x.m()

if __name__ == "__main__":
    print(g(X()))
