from dataclasses import dataclass

@dataclass
class D:
    x: int

#@ ensures \result == 0
def f() -> int:
    d = D(**{"x": 5})
    return d.x

if __name__ == "__main__":
    print(f())
