class A:
    #@ requires True
    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1

class B(A):
    #@ requires True
    #@ ensures \result == 2
    #@ assigns \nothing
    def m(self) -> int:
        return 2

#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def use(a: A) -> int:
    return a.m()

#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def driver() -> int:
    b = B()
    return use(b)
