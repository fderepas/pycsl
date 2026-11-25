def mk() -> int:
    __getattr__ = 1
    return __getattr__


#@ ensures \result == 3
#@ assigns \nothing
def three() -> int:
    return 3
