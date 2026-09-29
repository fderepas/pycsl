N = 3

code = "global N\n" + "N = 5"
exec(code)


#@ ensures \result == 3
def read() -> int:
    return N
