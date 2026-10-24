F: float = 0.5
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    if F % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1, g()
