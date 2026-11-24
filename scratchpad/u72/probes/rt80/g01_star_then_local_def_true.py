from rt80_liba import *


#@ ensures \result == 2
#@ assigns \nothing
def helper() -> int:
    return 2


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return helper()

if __name__ == "__main__":
    print(g())
