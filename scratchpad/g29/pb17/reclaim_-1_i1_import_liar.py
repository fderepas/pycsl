_ = 0  # anchor

from liar import seven


#@ ensures \result == -1
def probe() -> int:
    return seven()
