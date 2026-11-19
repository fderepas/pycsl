#@ ensures \result == 0
#@ assigns \nothing
def f(n: int) -> int:
    s: str = "ab"
    a = "x"
    b = "y"
    joined = f"{a}-{b}"
    if joined == "x-y" and len(s) == 2:
        return 0
    return 1
