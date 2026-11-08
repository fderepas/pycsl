from dataclasses import dataclass

@dataclass
class P:
    x: float

#@ ensures \result == 1
def f() -> int:
    a = P(1.5)
    b = P(1.5)
    if a == b:
        return 1
    return 0
