from dataclasses import dataclass, InitVar

#@ class invariant self.x >= 0
@dataclass
class D:
    x: int
    k: InitVar[int]

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.x

if __name__ == "__main__":
    print(f(D(-1, 0)))
