import argparse


class C:
    K = 1

    def __init__(self) -> None:
        self.x: int = 1
        argparse.Namespace.__init__(self, K=[1])


#@ no_exception \all
def f(c: C) -> int:
    s = {c.K}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(C())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
