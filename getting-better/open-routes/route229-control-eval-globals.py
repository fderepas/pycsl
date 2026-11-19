N = 3


#@ ensures \result == 0
def rebind() -> int:
    code = "globals().update({'N': 5})"
    eval(code)
    return 0


#@ ensures \result == 3
def read() -> int:
    return N
