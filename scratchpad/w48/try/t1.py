#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a = "x"
    b = "y"
    joined = f"{a}-{b}"
    if joined == "x-y":
        return 0
    return 1
