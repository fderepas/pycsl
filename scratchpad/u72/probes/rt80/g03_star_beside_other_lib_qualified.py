from rt80_liba import *
import rt80_libb


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return rt80_libb.helper()

if __name__ == "__main__":
    print(g())
