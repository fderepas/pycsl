"""v13 AGREE — -1 // 2 is -1 (FLOOR). C-style truncation toward zero would give 0."""


#@ ensures \result == -1
#@ assigns \nothing
def f() -> int:
    a: int = -1
    b: int = 2
    return a // b


if __name__ == "__main__":
    print(f())
