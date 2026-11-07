import random
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    r = random.random()
    if r * 2 // 2 == r:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1, g()
