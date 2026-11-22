import u70libt


#@ ensures \result == 2
#@ assigns \nothing
def _h() -> int:
    return 2


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return u70libt.f()

if __name__ == "__main__":
    print(g())
