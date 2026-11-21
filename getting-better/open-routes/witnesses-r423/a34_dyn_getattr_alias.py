class R:
    def __init__(self) -> None:
        self.x: int = 1


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)


if __name__ == "__main__":
    T = type
    S = T("S", (R,), {"k": 5})
    try:
        r = f(S())
        if not (r == 0):
            print("VIOLATION ensures", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
