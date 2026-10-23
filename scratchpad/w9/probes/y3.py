_ = 0  # anchor
#@ requires True
#@ ensures \result == 0
def f() -> int:
    x = 0
    def inner() -> int:
        return 7
    x = inner()
    return x
if __name__ == "__main__":
    print(f())
