"""v15 AGREE — -7 % 3 is 2. C-style remainder would give -1."""


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    a: int = -7
    b: int = 3
    return a % b


if __name__ == "__main__":
    print(f())
