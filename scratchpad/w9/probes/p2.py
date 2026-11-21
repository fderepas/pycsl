_ = 0  # anchor
#@ requires True
#@ ensures \result == 0
def f() -> int:
    g = lambda x: x + 1
    if g:
        return 7
    return 0
if __name__ == "__main__":
    print(f())
