from dataclasses import dataclass, KW_ONLY as KO

@dataclass
class D:
    x: int
    _: KO
    y: int = 0

#@ no_exception \all
def f() -> int:
    d = D(1, 2)
    return d.x

if __name__ == "__main__":
    print(f())
