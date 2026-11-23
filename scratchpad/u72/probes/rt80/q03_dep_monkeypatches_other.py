import rt80_patch
import rt80_liba


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return rt80_liba.helper()

if __name__ == "__main__":
    print(g())
