#@ requires 1 <= y and y <= 1000
#@ requires 0 <= x and x <= y
#@ ensures \result >= 0 and \result <= 1000
#@ ensures \result == (x * 1000) // y
def hdiv(x: int, y: int) -> int:
    return (x * 1000) // y

# false postcondition: \result==0 is false (hdiv(a,1000) can be nonzero)
#@ requires 0 <= a and a <= 1000
#@ ensures \result == 0
def caller(a: int) -> int:
    return hdiv(a, 1000)
