_ = 0  # anchor


def risky(v: int) -> int:
    if v < 0:
        raise ValueError()
    return v
