for A in [0.5]:
    pass
#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    return A % 1 == 0

if __name__ == "__main__":
    assert g() == True, g()
