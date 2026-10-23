"""v25 AGREE — Python CHAINS comparisons: `5 > 3 > 1` is `5 > 3 and 3 > 1` = True (1). A left-associative model computes `(5 > 3) > 1` = `1 > 1` = False, so this operand triple separates the two readings."""


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: int = 5
    b: int = 3
    c: int = 1
    return a > b > c


if __name__ == "__main__":
    print(int(f()))
