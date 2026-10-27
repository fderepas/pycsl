import warnings


class R:
    def __init__(self) -> None:
        self.x: int = 1
        warnings.catch_warnings.__init__(self)


#@ ensures \result == 7
def f(r: R) -> int:
    return getattr(r, "_record", 7)


if __name__ == "__main__":
    try:
        r = f(R())
        if not (r == 7):
            print("VIOLATION ensures", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
