#@ ensures \result == 7
#@ assigns \nothing
def g() -> int:
    x = 1
    return 7 if x is True else 0

if __name__ == "__main__":
    assert g() == 7, g()
