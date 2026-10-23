from dataclasses import dataclass

@dataclass
class P:
    x: float

#@ ensures \result == 1
def f() -> int:
    a = P(float("nan"))
    if a == a:
        return 1
    return 0
