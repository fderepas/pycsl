from dataclasses import dataclass, InitVar as IV

@dataclass
class D:
    x: int
    k: IV[int]

#@ ensures \result == 5
def f() -> int:
    d = D(1, 5)
    return d.k

if __name__ == "__main__":
    print(f())
