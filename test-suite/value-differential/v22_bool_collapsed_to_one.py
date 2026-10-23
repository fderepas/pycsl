"""v22 DISAGREE — claims bools collapse to 1. CPython says 2. PyCSL must REFUSE."""


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: bool = True
    b: bool = True
    return a + b


if __name__ == "__main__":
    print(f())
