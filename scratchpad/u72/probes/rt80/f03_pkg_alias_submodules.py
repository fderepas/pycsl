import rt80pkg.a as pa
import rt80pkg.b as pb


#@ ensures \result == 2 or \result == 4
#@ assigns \nothing
def g() -> int:
    return pa.f() + pb.f()

if __name__ == "__main__":
    print(g())
