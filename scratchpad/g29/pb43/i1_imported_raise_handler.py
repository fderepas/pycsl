_ = 0  # anchor

from risky import risky


#@ ensures \result == 0
def probe() -> int:
    try:
        risky(-1)
    except ValueError:
        return 9
    return 0
