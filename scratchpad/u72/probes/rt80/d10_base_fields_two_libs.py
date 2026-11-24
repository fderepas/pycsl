import rt80_fld_a
import rt80_fld_b


class X(rt80_fld_a.Base):
    pass


class Y(rt80_fld_b.Base):
    pass


#@ ensures \result == 11
#@ assigns \nothing
def g() -> int:
    x = X()
    y = Y()
    return x.v + 10 * y.v

if __name__ == "__main__":
    print(g())
