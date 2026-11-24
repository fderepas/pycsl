from rt77liba import *
from rt77libb import *


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return helper()

if __name__ == "__main__":
    print(g())
