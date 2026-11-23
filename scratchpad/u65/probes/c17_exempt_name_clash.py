#@ \diverges
#@ ensures \result == 0
def inner(x: int) -> int:
    while True:
        pass
    return 0

#@ ensures \result == 1
def outer(y: int) -> int:
    #@ requires x > 0 and x < 0
    #@ ensures \result == 99
    def inner(x: int) -> int:
        return 1
    return 1
