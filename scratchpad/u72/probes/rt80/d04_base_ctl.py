import rt80_cls_a


class X(rt80_cls_a.Base):
    pass


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return X().m()

if __name__ == "__main__":
    print(g())
