import argparse


class R:
    def __init__(self) -> None:
        self.x: int = 1


def init(r: R) -> None:
    argparse.Namespace.__init__(r, k=5)


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)


if __name__ == "__main__":
    r = R()
    init(r)
    try:
        r = f(r)
        if not (r == 0):
            print("VIOLATION ensures", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
