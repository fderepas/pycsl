from dataclasses import dataclass, field

@dataclass
class D:
    x: int = field(kw_only=True)
    y: int = 0

#@ no_exception \all
def f() -> int:
    d = D(5)
    return d.y

if __name__ == "__main__":
    print(f())
