from dataclasses import dataclass

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {(d, 1)}
    return 1

if __name__ == "__main__":
    print(g(D(1)))
