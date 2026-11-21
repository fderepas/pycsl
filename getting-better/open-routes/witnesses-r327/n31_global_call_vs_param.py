#@ ensures \result == 5
#@ assigns \nothing
def mk() -> int:
    return 5
K = mk()
#@ requires k == 1
#@ ensures \result == 1
#@ assigns \nothing
def g(k: int) -> int:
    return K

if __name__ == "__main__":
    assert g(1) == 1, g(1)
