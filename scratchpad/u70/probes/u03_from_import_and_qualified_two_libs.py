import rt77liba
from rt77libb import helper


#@ ensures \result == 2 or \result == 4
#@ assigns \nothing
def g() -> int:
    return rt77liba.helper() + helper()

if __name__ == "__main__":
    print(g())
