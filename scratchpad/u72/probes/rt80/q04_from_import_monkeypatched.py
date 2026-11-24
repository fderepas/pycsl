import rt80_patch
from rt80_liba import helper


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return helper()

if __name__ == "__main__":
    print(g())
