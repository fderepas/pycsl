"""v19 DISAGREE — the C-TRUNCATION answer 0. CPython says -1. PyCSL must REFUSE."""


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a: int = -1
    b: int = 2
    return a // b


if __name__ == "__main__":
    print(f())
