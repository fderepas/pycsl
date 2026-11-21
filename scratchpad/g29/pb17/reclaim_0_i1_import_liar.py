_ = 0  # anchor

from liar import seven


#@ ensures \result == 0
def probe() -> int:
    return seven()
