_ = 0  # anchor
#@ requires True
#@ ensures \result == 0
def f() -> int:
    x = 0
    if (y := 7) > 0:
        x = y
    return x
if __name__ == "__main__":
    print(f())
