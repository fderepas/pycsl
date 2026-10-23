_ = 0  # anchor
#@ requires True
#@ ensures \result == 0
def f() -> int:
    i = 0
    r = 0
    #@ loop invariant 0 <= i and i <= 1
    #@ loop variant 1 - i
    while i < 1:
        i = i + 1
    else:
        r = 7
    return r
if __name__ == "__main__":
    print(f())
