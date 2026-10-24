def mk() -> list[int]:
    return [1, 2]
X = mk()
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    if X * 0 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1, g()
