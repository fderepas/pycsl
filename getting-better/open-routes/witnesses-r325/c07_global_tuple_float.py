T = (0.5, 1)
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    if T[0] % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1, g()
