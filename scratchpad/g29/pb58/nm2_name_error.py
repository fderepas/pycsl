_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    if undefined_name_xyz:
        return 1
    return 0
