"""v01 AGREE — Python floor division with a NEGATIVE DIVISOR is -4, not the Euclidean -3."""


#@ ensures \result == -4
#@ assigns \nothing
def f() -> int:
    a: int = 7
    b: int = -2
    return a // b


if __name__ == "__main__":
    print(f())
