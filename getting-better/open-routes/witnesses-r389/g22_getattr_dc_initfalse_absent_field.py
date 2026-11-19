from dataclasses import dataclass, field


@dataclass
class R:
    x: int = 1

    def __post_init__(self) -> None:
        setattr(self, "k", 5)


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)


if __name__ == "__main__":
    v = f(R())
    print("VIOLATION f =", v) if v != 0 else print("no violation")
