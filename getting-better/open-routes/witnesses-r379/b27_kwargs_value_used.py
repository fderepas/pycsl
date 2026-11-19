from dataclasses import dataclass

@dataclass
class D:
    x: int

#@ ensures \result == 0
def f() -> int:
    kw = {"x": 5}
    d = D(**kw)
    return d.x

if __name__ == "__main__":
    print(f())
