#@ ensures \result == 1
#@ assigns \nothing
def g(n: int) -> int:
    s = 0
    #@ loop invariant (s == 0 and _idx_i == 0) or (s == 1 and _idx_i == 11)
    for i in range(3):
        s = s + 1
        _idx_i = 10
    return s

if __name__ == "__main__":
    assert g(0) == 1, g(0)
