from dataclasses import dataclass

@dataclass
class P:
    x: int

#@ ensures \result == 1
def f() -> int:
    a = P(1)
    b = P(1)
    if a == b:
        return 1
    return 0
