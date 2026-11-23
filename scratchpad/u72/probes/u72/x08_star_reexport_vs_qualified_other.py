from rt80_reex import *
import rt80_base2


#@ ensures \result == 4
#@ assigns \nothing
def g() -> int:
    return f() + rt80_base2.f()

if __name__ == "__main__":
    print(g())
