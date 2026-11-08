import argparse


class R:
    def __init__(self) -> None:
        self.x: int = 1
        argparse.Namespace.__init__(self, x=[1])


#@ no_exception \all
def f(r: R) -> int:
    s = {r.x}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(R())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
