#@ requires n > 0
#@ ensures \result == 0
#@ assigns \nothing
def g(n: int) -> int:
    Y = n
    y = 0
    return Y

if __name__ == "__main__":
    assert g(2) == 0, g(2)
