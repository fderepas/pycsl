class A:
    #@ requires True
    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1

class B(A):
    pass

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def driver() -> int:
    b = B()
    return b.m()
