_ = 0  # anchor
#@ requires True
#@ ensures \result == 0
def f() -> int:
    s = {1, 2, 3}
    if s:
        return 7
    return 0
if __name__ == "__main__":
    print(f())
