from dataclasses import dataclass

@dataclass(frozen=True)
class A:
    z: "Z"

@dataclass
class Z:
    n: int

#@ no_exception \all
#@ ensures \result == 1
def g(a: A) -> int:
    s = {a}
    return 1

if __name__ == "__main__":
    print(g(A(Z(1))))
