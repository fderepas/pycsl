#@ ensures \result == 1
def f() -> int:
    a = float("nan")
    if a == a:
        return 1
    return 0
