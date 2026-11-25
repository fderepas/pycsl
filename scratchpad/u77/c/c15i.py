from dataclasses import dataclass


@dataclass
class B:
    a: int

    #@ ensures \result == 0
    #@ assigns self.a
    def total(self) -> int:
        self.a = self.a + 1
        return 0


@dataclass
class R(B):
    b: int


@dataclass
class S:
    n: int

    #@ ensures \result == self.n
    #@ assigns \nothing
    def total(self) -> int:
        return self.n


#@ ensures \result == 0
#@ assigns \nothing
def f(r: R) -> int:
    return r.total()


if __name__ == "__main__":
    r = R(1, 2); print(f(r), r)
