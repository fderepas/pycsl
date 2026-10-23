_ = 0  # anchor

import errlib


class Sub(errlib.MyErr):
    pass


#@ ensures \result == 0
def probe() -> int:
    try:
        raise Sub()
    except errlib.MyErr:
        return 9
    return 0
