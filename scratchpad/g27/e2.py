r"""E2 — carrier of MY #140 repair: a MODULE function with an unsupplied default (the module
path binds defaults before the wrap, so this should have been fenced at HEAD already)."""
_ = 0  # anchor


#@ raises ValueError when k < 0
#@ assigns \nothing
def g(k: int = -1) -> int:
    m = k
    if m < 0:
        raise ValueError
    return m


#@ requires k >= 0
#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    return g()
