_ = 0  # anchor
#@ requires True
#@ ensures \result == 0
def f() -> int:
    x = (1, 2)
    if x[0] == 1:
        return 7
    return 0
if __name__ == "__main__":
    print(f())
