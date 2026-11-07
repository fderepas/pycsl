#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a = "x"
    b = "y"
    j = a + b
    if j == "xy":
        return 0
    return 1
