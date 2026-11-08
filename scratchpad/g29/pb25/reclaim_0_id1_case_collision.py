_ = 0  # anchor


#@ ensures \result == 0
def Foo() -> int:
    return 1


#@ ensures \result == 0
def foo() -> int:
    return 2


#@ ensures \result == 0
def probe() -> int:
    return foo()
