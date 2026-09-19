_ = 0  # anchor


class MyErr(Exception):
    pass


class _MyErr(Exception):
    pass


#@ ensures \result == 9
def probe() -> int:
    try:
        raise _MyErr()
    except MyErr:
        return 9
    return 0
