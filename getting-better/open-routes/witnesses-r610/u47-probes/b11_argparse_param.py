# u47: a PARAMETER named `argparse` shadows the module; `argparse.ArgumentParser()` is the
# user method (an effect the law-free model drops).
import argparse


class A:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns self.n
    def ArgumentParser(self) -> int:
        self.n = self.n + 1
        return 0


#@ ensures argparse.n == \old(argparse.n)
def f(argparse: A) -> int:
    try:
        p = argparse.ArgumentParser()
    except (AttributeError, IndexError, TypeError, ValueError):
        return 0
    return 1


if __name__ == "__main__":
    a = A()
    f(a)
    print("VIOLATION contract" if a.n != 0 else "result", a.n)
