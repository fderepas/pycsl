from dataclasses import dataclass

class M:
    __hash__ = None

class N:
    pass

class Z(N, M):
    pass

@dataclass(frozen=True)
class D:
    z: Z

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D(Z())))
