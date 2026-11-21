class A:
    #@ requires True
    #@ ensures \result == 1
    #@ assigns \nothing
    def kind(self) -> int:
        return 1

class B(A):
    #@ requires True
    #@ ensures \result == 2
    #@ assigns \nothing
    def kind(self) -> int:
        return 2

#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    b = B()
    if b.kind() == 2:
        return 0
    return 1
