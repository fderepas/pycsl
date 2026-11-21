EPS = 0.5
#@ ensures \result == True
#@ assigns \nothing
def g(x: int) -> bool:
    e, _ = EPS, 0
    return x < e or x >= e + 1 or x == e

if __name__ == "__main__":
    assert g(1) == True, g(1)
