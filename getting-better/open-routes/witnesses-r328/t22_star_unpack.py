A, *REST = [0.5, 1]
#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    return A * 2 == 2 * A and A % 1 == 0

if __name__ == "__main__":
    assert g() == True, g()
