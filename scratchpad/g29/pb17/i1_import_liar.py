_ = 0  # anchor

from liar import seven


#@ ensures \result == 7
def probe() -> int:
    return seven()
