EPS = 0.5
#@ requires x >= 0
#@ ensures \result == True
#@ assigns \nothing
def g(x: int) -> bool:
    return x < EPS or x >= EPS + 1 or x == EPS

if __name__ == "__main__":
    assert g(1) == True, g(1)
