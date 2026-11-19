class A:
    def __init__(self, x: int) -> None:
        self.x: int = x

    #@ no_exception \all
    def __hash__(self) -> int:
        return 0

    #@ no_exception \all
    def __eq__(self, other: "A") -> bool:
        return self.x == other.x


#@ no_exception \all
def f(a: A) -> int:
    s = {a, False}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(A(1))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
