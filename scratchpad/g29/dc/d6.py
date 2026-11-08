r"""G29 DC6 — dataclass keyword-only field whose default is a MODULE CONSTANT, omitted."""
from dataclasses import dataclass, field
_ = 0  # anchor
K = 5


@dataclass
class P:
    x: int = field(kw_only=True, default=K)


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    p = P()
    return p.x


if __name__ == "__main__":
    print("CPython:", probe())
