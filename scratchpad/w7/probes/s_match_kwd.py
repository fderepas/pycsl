#@ datatype Shape = Circle(r: int) | Sq(a: int)

#@ requires True
#@ ensures \result == 7
#@ assigns \nothing
def f(s: Shape) -> int:
    r: int = 0
    match s:
        case Circle(r=0):
            r = 7
        case _:
            r = 0
    return r
