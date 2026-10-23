G: int = 1

#@ requires True
#@ ensures \result == 0
#@ assigns G
def bump() -> int:
    global G
    G = 7
    return 0

#@ ensures \result == 1
def f() -> int:
    assert bump() == 0
    return G
if __name__ == "__main__":
    print(f())
