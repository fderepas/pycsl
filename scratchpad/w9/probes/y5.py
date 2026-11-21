_ = 0  # anchor
#@ requires \length(a) >= 3
#@ ensures \result == 0
#@ assigns a[0..2]
def f(a: list) -> int:
    a[0:2] = [7, 7]
    return a[0]
if __name__ == "__main__":
    print(f([0, 0, 0]))
