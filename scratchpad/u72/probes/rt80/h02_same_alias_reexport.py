import rt80_base as L
import rt80_reex2 as L


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return L.f()

if __name__ == "__main__":
    print(g())
