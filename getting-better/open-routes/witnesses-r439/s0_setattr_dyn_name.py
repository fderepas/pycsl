class R:
    def __init__(self, nm: str) -> None:
        self.x: int = 1
        setattr(self, nm, [1])

#@ no_exception \all
def f(r: R) -> int:
    s = {r.x}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(R("x"))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
