#@ ensures \result == 0
#@ assigns \nothing
def g(n: int) -> int:
    _idx_i = 5
    s = 0
    #@ loop invariant s == 0
    for i in range(1):
        s = s + _idx_i
    return s

if __name__ == "__main__":
    assert g(0) == 0, g(0)
