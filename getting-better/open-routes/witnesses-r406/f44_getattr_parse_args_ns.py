import argparse


class R:
    def __init__(self) -> None:
        self.x: int = 1
        p = argparse.ArgumentParser()
        p.add_argument("--k", type=int, default=5)
        p.parse_args([], namespace=self)


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)


if __name__ == "__main__":
    try:
        r = f(R())
        if not (r == 0):
            print("VIOLATION ensures", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
