N = 3


#@ ensures \result == 0
def rebind() -> int:
    exec("global N\nN = 5")
    return 0


#@ ensures \result == 3
def read() -> int:
    return N
