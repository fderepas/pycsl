from dataclasses import dataclass

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    t = (d, 2)
    h = hash(t)
    return 1

if __name__ == "__main__":
    print(g(D(1)))
