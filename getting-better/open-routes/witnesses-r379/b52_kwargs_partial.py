from dataclasses import dataclass

@dataclass
class D:
    x: int
    y: int

#@ ensures \result == 0
def f() -> int:
    kw = {"y": 7}
    d = D(1, **kw)
    return d.y

if __name__ == "__main__":
    print(f())
