
#@ ensures \result == True
#@ assigns \nothing
def g(n: int) -> bool:
    s = repr(n)
    return s * 0 == 0

if __name__ == "__main__":
    assert g(1) == True
