from dataclasses import dataclass

@dataclass
class C:
    v: int

#@ ensures \result == 1
def f() -> int:
    a = C(1)
    b = a
    b.v = 2
    return a.v
if __name__ == "__main__":
    print(f())
