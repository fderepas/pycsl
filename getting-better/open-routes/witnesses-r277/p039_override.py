class A:
    def __init__(self) -> None:
        self.v: int = 0
    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1

class B(A):
    #@ assigns \nothing
    def m(self) -> int:
        return 2

#@ ensures \result == 1
#@ assigns \nothing
def use(a: A) -> int:
    return a.m()

if __name__ == "__main__":
    print(use(B())); assert use(B()) == 1
