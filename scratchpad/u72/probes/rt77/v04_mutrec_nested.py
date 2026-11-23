#@ ensures \result == 0
def outer(y: int) -> int:
    #@ requires n >= 0
    #@ ensures \result >= 0
    #@ \variant n
    def p(n: int) -> int:
        if n <= 0:
            return 0
        return q(n - 1)

    #@ requires n >= 0 and n < 0
    #@ ensures \result == 99
    #@ \variant n
    def q(n: int) -> int:
        if n <= 0:
            return 1
        return p(n - 1)
    return 0
