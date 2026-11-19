from dataclasses import dataclass

@dataclass
class D:
    x: int

#@ no_exception \all
def f() -> int:
    kw = {"x": 1, "z": 2}
    d = D(**kw)
    return d.x

if __name__ == "__main__":
    print(f())
