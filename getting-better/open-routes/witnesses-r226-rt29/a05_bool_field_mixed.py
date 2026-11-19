from dataclasses import dataclass

#@ class invariant self.x >= 0 or self.ok
@dataclass
class D:
    x: int
    ok: bool

#@ ensures \result >= 0
def f(d: D) -> int:
    if d.ok:
        return 0
    return d.x

if __name__ == "__main__":
    assert f(D(-1, False)) >= 0
