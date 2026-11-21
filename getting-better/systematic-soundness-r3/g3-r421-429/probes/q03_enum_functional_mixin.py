import enum


class B:
    def __init__(self) -> None:
        self.x: int = 1


#@ no_exception \all
def f(b: B) -> int:
    s = {b}
    return len(s)


if __name__ == "__main__":
    D = enum.Enum("D", "A", type=B)
    print(f(B()))
