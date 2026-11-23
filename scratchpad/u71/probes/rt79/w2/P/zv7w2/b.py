import hw792


def _two() -> int:
    return 2


print("b.py loaded")
hw792.one = _two
