#@ ensures \result == 0
def outer() -> int:
    #@ ensures \result == 1
    def inner() -> int:
        return 2
    return 0
