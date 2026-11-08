_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    """FALSE OF THE PROGRAM: the loop variable survives the loop with value 2,
    so Python returns 2."""
    i = 0
    #@ loop invariant 0 <= i and i <= 3
    #@ loop variant 3 - i
    for i in range(3):
        pass
    return i
