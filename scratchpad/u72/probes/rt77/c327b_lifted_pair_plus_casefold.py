#@ ensures \result == 1
def p() -> int:
    def f() -> int:
        return 1
    return f()


#@ ensures \result == 2
def q() -> int:
    def f() -> int:
        return 2
    return f()


#@ ensures \result == 3
#@ assigns \nothing
def F() -> int:
    return 3
