#@ requires (a == 0) or (a == 1)
#@ requires (b == 0) or (b == 1)
#@ ensures \result == ((a + b) - (2 * (a * b)))
#@ assigns \nothing
def bool_xor(a: int, b: int) -> int:
    return (a + b) - 2 * (a * b)
