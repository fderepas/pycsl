r"""G29 DC7 — dataclass keyword-only field with a TRUE default, omitted."""
from dataclasses import dataclass, field
_ = 0  # anchor


@dataclass
class P:
    x: int = field(kw_only=True, default=True)


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    p = P()
    return p.x


if __name__ == "__main__":
    print("CPython:", probe())
