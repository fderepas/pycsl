#@ requires True
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    x: int = 1
    try:
        x = 2
    except ValueError:
        x = 9
    finally:
        x = 3
    return x
