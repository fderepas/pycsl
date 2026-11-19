#@ ensures \result == 7
#@ assigns \nothing
def g() -> int:
    a = "a"
    b = a + "b"
    c = "ab"
    return 7 if b is c else 0

if __name__ == "__main__":
    assert g() == 7, g()
