from dataclasses import dataclass

@dataclass(frozen=True)
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 5
def f(d: D) -> int:
    d.x = 5
    return d.x

if __name__ == "__main__":
    print(f(D(1)))
