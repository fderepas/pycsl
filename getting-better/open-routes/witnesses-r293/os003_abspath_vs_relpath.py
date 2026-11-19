import os

#@ ensures \result == 1
def f(s: str) -> int:
    r1 = os.path.relpath(s, "/usr")
    os.chdir("/")
    r2 = os.path.relpath(s, "/usr")
    #@ check r1 == r2
    return 1

if __name__ == "__main__":
    os.chdir("/tmp")
    a = os.path.relpath("x", "/usr")
    os.chdir("/")
    b = os.path.relpath("x", "/usr")
    assert a == b, (a, b)
