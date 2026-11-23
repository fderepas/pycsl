import zv7g1


#@ ensures \result == 5
def k() -> int:
    return 5


def _two() -> int:
    return 2


print("c.py loaded")
zv7g1.b = _two
