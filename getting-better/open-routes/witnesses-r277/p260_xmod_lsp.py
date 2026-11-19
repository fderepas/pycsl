from rt6lib.base import A, use

class B(A):
    #@ ensures \result == 2
    #@ assigns \nothing
    def m(self) -> int:
        return 2

#@ ensures \result == 1
#@ assigns \nothing
def g(a: A) -> int:
    return use(a)

if __name__ == "__main__":
    print(g(B())); assert g(B()) == 1
