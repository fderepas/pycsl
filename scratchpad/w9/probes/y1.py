_ = 0  # anchor
#@ requires True
#@ ensures \result == 0
def f() -> int:
    d = {}
    d[1] = 7
    del d[1]
    d[1] = 7
    return d[1]
if __name__ == "__main__":
    print(f())
