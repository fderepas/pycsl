r"""G29 EN1 — a plain `Enum` member compared with its int value is NOT equal (IntEnum would be)."""
from enum import Enum
_ = 0  # anchor


class Color(Enum):
    RED = 1
    GREEN = 2


#@ ensures \result == 1
def probe() -> int:
    if Color.RED == 1:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
