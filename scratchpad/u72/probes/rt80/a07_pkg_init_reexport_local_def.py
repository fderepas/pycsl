import rt80pkg2


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    return 2


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return rt80pkg2.f()

if __name__ == "__main__":
    print(g())
