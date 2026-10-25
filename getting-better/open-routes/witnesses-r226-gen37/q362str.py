from dataclasses import dataclass

#@ class invariant self.x >= 0
@dataclass
class D:
    x: int
    s: str

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.x

if __name__ == "__main__":
    assert f(D(-1, "a")) >= 0
