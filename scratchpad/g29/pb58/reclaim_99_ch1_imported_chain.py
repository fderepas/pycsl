_ = 0  # anchor

from chainlib import mid


#@ ensures \result == 99
def probe() -> int:
    return mid(5, 1, 9)
