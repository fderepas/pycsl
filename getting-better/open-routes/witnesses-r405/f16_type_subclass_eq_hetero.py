class B:
    def __init__(self) -> None:
        self.x: int = 1


#@ no_exception \all
def f(b: B, c: B) -> int:
    s = {b, c}
    return len(s)


if __name__ == "__main__":
    D = type("D", (B,), {"__hash__": lambda s: 0, "__eq__": lambda s, o: 1 // 0})
    try:
        r = f(D(), D())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
