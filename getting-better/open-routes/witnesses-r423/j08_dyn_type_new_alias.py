class B:
    def __init__(self) -> None:
        self.x: int = 1


#@ no_exception \all
def f(b: B) -> int:
    s = {b}
    return len(s)


if __name__ == "__main__":
    tn = type.__new__
    D = tn(type, "D", (B,), {"__hash__": None})
    try:
        r = f(D())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
