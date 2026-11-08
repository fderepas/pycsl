r"""G29 DC8 — dataclass POSITIONAL field with a negative default, omitted."""
from dataclasses import dataclass
_ = 0  # anchor


@dataclass
class P:
    x: int = -5


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    p = P()
    return p.x


if __name__ == "__main__":
    print("CPython:", probe())
