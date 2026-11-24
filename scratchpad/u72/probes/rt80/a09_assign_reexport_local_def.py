import rt80_reex3


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return 1


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return rt80_reex3.f()

if __name__ == "__main__":
    print(g())
