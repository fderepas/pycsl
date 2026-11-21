from dataclasses import dataclass, KW_ONLY
K = KW_ONLY

@dataclass
class D:
    x: int
    _: K
    y: int = 0

#@ no_exception \all
def f(d: D) -> int:
    return d._

if __name__ == "__main__":
    print(f(D(1)))
