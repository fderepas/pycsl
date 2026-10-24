
#@ ensures \result == True
#@ assigns \nothing
def g(z: complex) -> bool:
    return z * z == 0 or z * z != -1

if __name__ == "__main__":
    assert g(complex(0, 1)) == True
