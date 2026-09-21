def helper(x: int) -> int:
    if x < 0:
        raise ValueError("neg")
    return x


#@ no_exception ValueError
#@ ensures \result == 5
def probe() -> int:
    return helper(0 - 5)
