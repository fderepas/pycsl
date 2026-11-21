from dataclasses import dataclass, InitVar
IV = InitVar

@dataclass
class D:
    x: int
    k: IV[int]

#@ no_exception \all
def f(d: D) -> int:
    return d.k

if __name__ == "__main__":
    print(f(D(1, 5)))
