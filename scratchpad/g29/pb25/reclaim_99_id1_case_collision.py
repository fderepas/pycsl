_ = 0  # anchor


#@ ensures \result == 99
def Foo() -> int:
    return 1


#@ ensures \result == 99
def foo() -> int:
    return 2


#@ ensures \result == 99
def probe() -> int:
    return foo()
