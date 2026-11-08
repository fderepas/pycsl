r"""G29 EN2 — `auto()` values start at 1."""
from enum import Enum, auto
_ = 0  # anchor


class Color(Enum):
    RED = auto()
    GREEN = auto()


#@ ensures \result == 0
def probe() -> int:
    return Color.RED.value


if __name__ == "__main__":
    print("CPython:", probe())
