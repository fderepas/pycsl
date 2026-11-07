import os

#@ ensures \result == 1
def f() -> int:
    r1 = os.path.relpath("a", "/")
    os.chdir("/tmp")
    r2 = os.path.relpath("a", "/")
    #@ check r1 == r2
    return 1

if __name__ == "__main__":
    os.chdir("/home")
    r1 = os.path.relpath("a", "/")
    os.chdir("/tmp")
    r2 = os.path.relpath("a", "/")
    assert r1 == r2, (r1, r2)
