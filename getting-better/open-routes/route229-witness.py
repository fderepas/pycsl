N = 3


#@ ensures \result == 0
def rebind() -> int:
    code = "global N\nN = 5"
    exec(code)
    return 0


#@ ensures \result == 3
def read() -> int:
    return N
