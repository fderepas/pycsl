from dataclasses import dataclass


@dataclass
class R:
    a: int
    b: int


#@ requires True
#@ ensures True
#@ assigns \nothing
def f(r: R) -> None:
    r.b = 5


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def g() -> int:
    r = R(1, 0)
    f(r)
    return r.b


if __name__ == "__main__":
    print("CPython g() =", g())
