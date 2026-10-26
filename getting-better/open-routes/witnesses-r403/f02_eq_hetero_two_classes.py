class A:
    def __init__(self, x: int) -> None:
        self.x: int = x

    #@ no_exception \all
    def __hash__(self) -> int:
        return 0

    #@ no_exception \all
    def __eq__(self, other: "A") -> bool:
        return self.x == other.x


class B:
    def __init__(self) -> None:
        self.y: int = 0

    #@ no_exception \all
    def __hash__(self) -> int:
        return 0


#@ no_exception \all
def f(a: A, b: B) -> int:
    s = {a, b}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(A(1), B())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
