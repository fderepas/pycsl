from dataclasses import dataclass, field as fld

@dataclass
class D:
    x: int = fld(default=7)

#@ ensures \result == 0
def f() -> int:
    d = D()
    return d.x

if __name__ == "__main__":
    print(f())
