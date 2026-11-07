#@ ensures \result == 7
#@ assigns \nothing
def g() -> int:
    x = 1
    if not (x is True):
        return 0
    return 7

if __name__ == "__main__":
    assert g() == 7, g()
