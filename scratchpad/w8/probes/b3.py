#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def driver(xs) -> int:
    try:
        v: int = 1 // 0
        return 1
    except ZeroDivisionError:
        return 2
