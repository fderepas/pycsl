from dataclasses import dataclass, field

#@ class invariant self.n >= 0
@dataclass
class D:
    x: int
    n: int = field(default_factory=lambda: -1, init=False)

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.n

if __name__ == "__main__":
    assert f(D(1)) >= 0
