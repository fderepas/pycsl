from dataclasses import dataclass

@dataclass(init=False)
class D:
    x: int = 4

#@ no_exception \all
def f() -> int:
    d = D(1)
    return d.x

if __name__ == "__main__":
    print(f())
