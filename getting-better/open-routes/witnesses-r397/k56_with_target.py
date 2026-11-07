import contextlib


class R:
    def __init__(self) -> None:
        self.x: int = 1
        with contextlib.nullcontext(5) as self.k:
            pass


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)


if __name__ == "__main__":
    try:
        print("result", f(R()))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
