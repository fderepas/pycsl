r"""G29 CD7 — dataclass structural equality."""
from dataclasses import dataclass
_ = 0  # anchor


@dataclass
class P:
    x: int
    y: int


#@ ensures \result == False
def probe() -> bool:
    return P(1, 2) == P(1, 2)


if __name__ == "__main__":
    print("CPython:", probe())
