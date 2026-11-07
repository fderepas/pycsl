#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    s = "abc"
    if s[10:20] == "":
        return 1
    return 0
