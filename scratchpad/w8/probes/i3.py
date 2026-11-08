class A:
    #@ requires True
    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1

class B(A):
    #@ requires True
    #@ ensures \result == 3
    #@ assigns \nothing
    def m(self) -> int:
        return super().m() + 2

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def driver() -> int:
    b = B()
    return b.m()
