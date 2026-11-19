class B:
    #@ requires True
    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1

class D(B):
    #@ requires True
    #@ ensures \result == 2
    #@ assigns \nothing
    def m(self) -> int:
        return 2

#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def driver() -> int:
    d = D()
    return d.m()
