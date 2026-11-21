"""v14 AGREE — -1 % 2 is 1 (follows the DIVISOR's sign). C-style would give -1."""


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: int = -1
    b: int = 2
    return a % b


if __name__ == "__main__":
    print(f())
