from enum import Enum
_ = 0  # anchor


class Color(Enum):
    RED = 1
    GREEN = 2


#@ ensures \result == 0
def probe() -> int:
    c = Color.GREEN
    return c.value
