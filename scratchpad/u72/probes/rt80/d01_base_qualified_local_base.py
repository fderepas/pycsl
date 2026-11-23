import rt80_cls_a


class Base:
    def __init__(self) -> None:
        self.v = 0

    #@ ensures \result == 2
    #@ assigns \nothing
    def m(self) -> int:
        return 2


class X(rt80_cls_a.Base):
    pass


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return X().m()

if __name__ == "__main__":
    print(g())
