r"""G29 EN3 — an Enum ALIAS: a second name with the same value IS the first member."""
from enum import Enum
_ = 0  # anchor


class Color(Enum):
    RED = 1
    CRIMSON = 1


#@ ensures \result == 0
def probe() -> int:
    if Color.RED is Color.CRIMSON:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
