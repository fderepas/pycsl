class A:
    def __init__(self) -> None:
        self.v: int = 0
    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1

class B(A):
    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        if self.v == 0:
            raise ValueError("x")
        return 1

#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def use(a: A) -> int:
    return a.m()

if __name__ == "__main__":
    print(use(B()))
