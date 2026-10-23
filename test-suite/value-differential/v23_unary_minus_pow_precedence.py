"""v23 AGREE — `**` binds TIGHTER than unary minus, so `-2 ** 2` is -(2**2) = -4, not (-2)**2 = 4."""


#@ ensures \result == -4
#@ assigns \nothing
def f() -> int:
    return -2 ** 2


if __name__ == "__main__":
    print(f())
