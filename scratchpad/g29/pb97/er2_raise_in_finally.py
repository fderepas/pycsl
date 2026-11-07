_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    try:
        return 1
    finally:
        raise ValueError()
