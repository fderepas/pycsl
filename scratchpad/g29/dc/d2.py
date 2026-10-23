r"""G29 DC2 — `dataclasses.replace(p, x=5)`."""
import dataclasses
from dataclasses import dataclass
_ = 0  # anchor


@dataclass
class P:
    x: int = 0


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    p = P(1)
    q = dataclasses.replace(p, x=5)
    return q.x


if __name__ == "__main__":
    print("CPython:", probe())
