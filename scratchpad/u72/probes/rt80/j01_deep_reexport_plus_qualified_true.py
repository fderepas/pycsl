from rt80_reex import f
import rt80_base


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return f() + rt80_base.f()

if __name__ == "__main__":
    print(g())
