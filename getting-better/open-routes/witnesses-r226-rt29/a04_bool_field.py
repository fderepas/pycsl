from dataclasses import dataclass

#@ class invariant self.ok == True
@dataclass
class D:
    x: int
    ok: bool

#@ ensures \result == True
def f(d: D) -> bool:
    return d.ok

if __name__ == "__main__":
    assert f(D(1, False)) == True
