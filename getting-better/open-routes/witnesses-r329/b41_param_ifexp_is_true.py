#@ requires n == 1
#@ ensures \result == 7
#@ assigns \nothing
def g(n: int) -> int:
    return 7 if n is True else 0

if __name__ == "__main__":
    assert g(1) == 7, g(1)
