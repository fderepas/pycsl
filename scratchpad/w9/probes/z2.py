_ = 0  # anchor
#@ requires True
#@ ensures \result == 0
def f() -> int:
    a = 0
    b = 0
    a = b = 7
    return a
if __name__ == "__main__":
    print(f())
