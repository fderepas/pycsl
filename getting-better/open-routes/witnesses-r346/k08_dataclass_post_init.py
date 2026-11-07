from dataclasses import dataclass

#@ class invariant self.x >= 0
@dataclass
class D:
    x: int
    def __post_init__(self) -> None:
        self.x = -1

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.x

if __name__ == "__main__":
    print(f(D(3)))
