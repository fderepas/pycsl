from dataclasses import dataclass, InitVar

@dataclass
class D:
    x: int
    k: InitVar[int]

#@ no_exception \all
def f(d: D) -> int:
    return d.k

if __name__ == "__main__":
    print(f(D(1, 2)))
