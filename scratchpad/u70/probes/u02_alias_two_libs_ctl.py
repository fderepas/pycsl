from rt77liba import helper as ha
from rt77libb import helper


#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    return ha() + helper()

if __name__ == "__main__":
    print(g())
