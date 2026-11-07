F = 2.5
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    if int(F) == F:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1, g()
