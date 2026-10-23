_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = {"a": 1}.get("b")
    if x == 0:
        return 7
    return 0
