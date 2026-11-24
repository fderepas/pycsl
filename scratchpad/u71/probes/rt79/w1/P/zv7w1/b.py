import hw791


def _two() -> int:
    return 2


print("b.py loaded")
hw791.one = _two
