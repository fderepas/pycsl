_ = 0  # anchor
#@ requires True
#@ ensures \result == 0
def f() -> int:
    y = 7 if (1, 2) else 0
    return y - 7
if __name__ == "__main__":
    print(f())
