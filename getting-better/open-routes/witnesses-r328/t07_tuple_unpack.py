F = 0.5
#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    a, b = F, 1
    return a % 1 == 0

if __name__ == "__main__":
    assert g() == True, g()
