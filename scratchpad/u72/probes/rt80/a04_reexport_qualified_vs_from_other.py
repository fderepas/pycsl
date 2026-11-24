from rt80_base2 import f
import rt80_reex


#@ ensures \result == 4
#@ assigns \nothing
def g() -> int:
    return f() + rt80_reex.f()

if __name__ == "__main__":
    print(g())
