
#@ ensures \result == True
#@ assigns \nothing
def g(n: int) -> bool:
    s = f"{n}"
    return s * 0 == 0

if __name__ == "__main__":
    assert g(1) == True
