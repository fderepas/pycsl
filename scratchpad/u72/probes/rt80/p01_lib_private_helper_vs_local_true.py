import rt80_priv_a


#@ ensures \result == 5
#@ assigns \nothing
def _h() -> int:
    return 5


#@ ensures \result == 6
#@ assigns \nothing
def g() -> int:
    return rt80_priv_a.x() + _h()

if __name__ == "__main__":
    print(g())
