"""probe: builtins"""
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def test_builtins() -> int:
    n: int = abs(-3)
    m: int = max(1, 2)
    k: int = min(4, 2)
    if n == 3 and m == 2 and k == 2:
        return 0
    return 1
