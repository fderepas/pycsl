import hw793


def _two() -> int:
    return 2


print("b.py loaded")
hw793.one = _two
