_ = 0  # anchor

from exclib import Beta as _Alpha


class Alpha(Exception):
    pass


#@ ensures \result == 9
def probe() -> int:
    try:
        raise _Alpha()
    except Alpha:
        return 9
    return 0
