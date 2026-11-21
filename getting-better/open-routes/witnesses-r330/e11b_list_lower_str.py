
#@ requires len(xs) >= 1
#@ ensures \result == True
#@ assigns \nothing
def g(xs: list) -> bool:
    return xs[0] * 0 == 0

if __name__ == "__main__":
    assert g(["a"]) == True
