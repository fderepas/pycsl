_ = 0  # anchor

from risky import risky


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    risky(-1)
    return 0
