from dataclasses import dataclass

@dataclass
class Q:
    x: int

#@ ensures \result == q
def dup(q: Q) -> Q:
    return Q(q.x)
