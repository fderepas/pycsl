_ = 0  # anchor
#@ requires True
#@ ensures \result == 0
def f() -> int:
    r = 0
    #@ loop invariant True
    for i in range(1):
        r = r + 0
    else:
        r = 7
    return r
if __name__ == "__main__":
    print(f())
