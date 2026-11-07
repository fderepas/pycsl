#@ ensures \result == 1.0
#@ assigns \nothing
def f() -> float:
    return (0.1 + 0.2) / 0.3
