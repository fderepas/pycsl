_ = 0  # anchor
#@ requires True
#@ ensures \result == 0
def f() -> int:
    a = 1
    b = 7
    a, b = b, a
    return a
if __name__ == "__main__":
    print(f())
