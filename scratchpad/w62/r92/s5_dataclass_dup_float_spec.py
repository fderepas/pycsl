from dataclasses import dataclass

@dataclass
class P:
    x: float

#@ ensures \result == p
def dup(p: P) -> P:
    return P(p.x)
