_ = 0  # anchor

#@ requires True
#@ ensures \result == 0
def f() -> int:
    x = dict()
    if x:
        return 7
    return 0
if __name__ == "__main__":
    print(f())
