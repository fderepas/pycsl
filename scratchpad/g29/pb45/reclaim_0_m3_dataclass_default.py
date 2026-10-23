from dataclasses import dataclass
_ = 0  # anchor


@dataclass
class P:
    a: int = 3
    b: int = 4


#@ ensures \result == 0
def probe() -> int:
    p = P()
    return p.a + p.b + 1
