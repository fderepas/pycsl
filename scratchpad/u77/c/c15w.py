from dataclasses import dataclass


@dataclass
class R:
    a: int
    b: int

    #@ ensures \result == self.a + self.b
    #@ assigns \nothing
    def total(self) -> int:
        return self.a + self.b


@dataclass
class S:
    n: int

    #@ ensures \result == 0
    #@ assigns self.n
    def total(self) -> int:
        self.n = self.n + 1
        return 0


#@ ensures \result == 0
#@ assigns \nothing
def f(r: R, s: S) -> int:
    q = r
    if r.a > 0:
        q = s
    return q.total()


if __name__ == "__main__":
    r = R(1, 2); s = S(0); print(f(r, s), r, s)
