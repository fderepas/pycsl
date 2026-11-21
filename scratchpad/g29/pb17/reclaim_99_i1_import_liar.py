_ = 0  # anchor

from liar import seven


#@ ensures \result == 99
def probe() -> int:
    return seven()
