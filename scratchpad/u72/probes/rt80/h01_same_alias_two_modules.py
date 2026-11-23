import rt80_liba as L
import rt80_libb as L


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return L.helper()

if __name__ == "__main__":
    print(g())
