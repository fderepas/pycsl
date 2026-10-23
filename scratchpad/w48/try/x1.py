#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    n = 0
    try:
        n = 1
    finally:
        n = n + 2
    return n
