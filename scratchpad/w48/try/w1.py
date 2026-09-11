#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a = "xy"
    joined = f"{a}"
    if joined == a:
        return 0
    return 1
