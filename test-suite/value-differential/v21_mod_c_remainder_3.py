"""v21 DISAGREE — the C-REMAINDER answer -1. CPython says 2. PyCSL must REFUSE."""


#@ ensures \result == -1
#@ assigns \nothing
def f() -> int:
    a: int = -7
    b: int = 3
    return a % b


if __name__ == "__main__":
    print(f())
