#@ requires True
#@ ensures \result >= 0
def f(x: int) -> int:
    match x:
        case 0:
            return 0
        case _:
            return 1
