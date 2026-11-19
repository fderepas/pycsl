_ = 0  # anchor

import errlib


#@ ensures \result == 1
def probe() -> int:
    try:
        raise errlib.MyErr()
    except ValueError:
        return 9
    return 0
