"""v03 AGREE — -7 // -2 is 3 (floor of 3.5), not the Euclidean 4."""


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    a: int = -7
    b: int = -2
    return a // b


if __name__ == "__main__":
    print(f())
