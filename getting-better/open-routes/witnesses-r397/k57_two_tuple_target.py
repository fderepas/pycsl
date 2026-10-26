class R:
    def __init__(self) -> None:
        self.x: int = 1
        self.k, self.j = 5, 6


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "j", 0)


if __name__ == "__main__":
    try:
        print("result", f(R()))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
