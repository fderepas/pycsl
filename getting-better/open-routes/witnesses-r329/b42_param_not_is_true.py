#@ requires n == 1
#@ ensures \result == 7
#@ assigns \nothing
def g(n: int) -> int:
    if not (n is True):
        return 0
    return 7

if __name__ == "__main__":
    assert g(1) == 7, g(1)
