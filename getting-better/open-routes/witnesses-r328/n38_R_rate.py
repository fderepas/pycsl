RATE = 0.5
R = RATE
#@ requires x >= 0
#@ ensures \result == True
#@ assigns \nothing
def g(x: int) -> bool:
    if x == 0:
        return True
    return x < R or x >= R + 1 or x == R

if __name__ == "__main__":
    assert g(1) == True, g(1)
