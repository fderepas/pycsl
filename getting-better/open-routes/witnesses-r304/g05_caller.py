#@ requires x >= 0
#@ no_exception \all
#@ ensures \result == 0
def g(x: int) -> int:
    if x < 0:
        raise ValueError("neg")
    return 0

#@ no_exception \all
#@ ensures \result == 0
def h(y: int) -> int:
    return g(y * y)

if __name__ == "__main__":
    assert h(-3) == 0
