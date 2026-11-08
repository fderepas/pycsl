class B:
    def __init__(self) -> None:
        self.x: int = 1


#@ no_exception \all
def f(b: B) -> int:
    s = {b}
    return len(s)


if __name__ == "__main__":
    t = (type,)
    D = t[0]("D", (B,), {"__hash__": None})
    print(f(D()))
