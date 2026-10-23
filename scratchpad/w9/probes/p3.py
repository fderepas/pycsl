_ = 0  # anchor
#@ requires True
#@ ensures \result == 0
def f() -> int:
    n = 5
    s = f"{n}"
    if s:
        return 7
    return 0
if __name__ == "__main__":
    print(f())
