"""v02 AGREE — Python's % follows the DIVISOR's sign: 7 % -2 is -1, not the Euclidean 1."""


#@ ensures \result == -1
#@ assigns \nothing
def f() -> int:
    a: int = 7
    b: int = -2
    return a % b


if __name__ == "__main__":
    print(f())
