from dataclasses import dataclass

@dataclass
class D:
    x: int

class R:
    def __init__(self, d: D) -> None:
        self.d = d

#@ no_exception \all
#@ ensures \result == 1
def g(r: R) -> int:
    s = {r.d}
    return 1

if __name__ == "__main__":
    print(g(R(D(1))))
