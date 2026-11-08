from dataclasses import dataclass, field as fld

@dataclass
class D:
    x: int
    y: int = fld(init=False)

#@ no_exception \all
def f(d: D) -> int:
    return d.y

if __name__ == "__main__":
    print(f(D(1)))
