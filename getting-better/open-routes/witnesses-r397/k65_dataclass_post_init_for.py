from dataclasses import dataclass


@dataclass
class R:
    x: int

    def __post_init__(self) -> None:
        for self.k in [5]:
            pass


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)


if __name__ == "__main__":
    try:
        print("result", f(R(1)))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
