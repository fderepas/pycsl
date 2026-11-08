from dataclasses import dataclass, field as fld

@dataclass
class D:
    x: int = fld(default=0, kw_only=True)
    y: int = 0

#@ ensures \result == 5
def f() -> int:
    d = D(5)
    return d.x

if __name__ == "__main__":
    print(f())
