from dataclasses import dataclass

@dataclass(init=False)
class D:
    x: int

#@ no_exception \all
def f() -> int:
    d = D(1)
    return 1

if __name__ == "__main__":
    print(f())
