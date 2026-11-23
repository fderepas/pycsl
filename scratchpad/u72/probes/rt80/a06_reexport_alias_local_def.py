import rt80_reex as R


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    return 2


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return R.f()

if __name__ == "__main__":
    print(g())
