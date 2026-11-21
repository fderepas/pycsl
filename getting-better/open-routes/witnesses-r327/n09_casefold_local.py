#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    K = 7
    k = 3
    return K

if __name__ == "__main__":
    assert g() == 3, g()
