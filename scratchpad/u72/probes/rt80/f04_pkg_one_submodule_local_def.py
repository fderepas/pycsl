import rt80pkg.a


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    return 2


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return rt80pkg.a.f()

if __name__ == "__main__":
    print(g())
