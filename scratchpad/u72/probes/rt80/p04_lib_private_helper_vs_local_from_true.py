from rt80_priv_a import x


#@ ensures \result == 5
#@ assigns \nothing
def _h() -> int:
    return 5


#@ ensures \result == 6
#@ assigns \nothing
def g() -> int:
    return x() + _h()

if __name__ == "__main__":
    print(g())
