import rt80pkg.a
import rt80pkg.b


#@ ensures \result == 2 or \result == 4
#@ assigns \nothing
def g() -> int:
    return rt80pkg.a.f() + rt80pkg.b.f()

if __name__ == "__main__":
    print(g())
