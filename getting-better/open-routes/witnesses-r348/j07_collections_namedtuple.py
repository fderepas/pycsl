from collections import namedtuple
P = namedtuple("P", ["x", "y"])

#@ no_exception \all
#@ ensures \result == 5
def f(p: P) -> int:
    p.x = 5
    return 5

if __name__ == "__main__":
    print(f(P(1, 2)))
