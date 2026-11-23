import rt80_liba


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    return 2


#@ no_exception \all
#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return rt80_liba.f()

if __name__ == "__main__":
    print(g())
