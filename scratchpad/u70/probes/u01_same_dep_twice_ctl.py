import rt77lib_val
from rt77lib_val import val1


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return rt77lib_val.val1() + val1()

if __name__ == "__main__":
    print(g())
