_ = 0  # anchor


#@ ensures \result == 1
def Foo() -> int:
    return 1


#@ ensures \result == 1
def foo() -> int:
    return 2


#@ ensures \result == 1
def probe() -> int:
    return foo()
