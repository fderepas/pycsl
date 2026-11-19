from dataclasses import dataclass

@dataclass
class D:
    x: int

class R:
    def __init__(self, d: D) -> None:
        self.d = d

    #@ no_exception \all
    #@ ensures \result == 1
    def g(self) -> int:
        s = {self.d}
        return 1

if __name__ == "__main__":
    print(R(D(1)).g())
