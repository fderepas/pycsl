"""v11 DISAGREE — the BOOLEAN-COLLAPSE answer 1. CPython says 3. PyCSL must REFUSE."""


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: int = 5
    b: int = 3
    return a and b


if __name__ == "__main__":
    print(f())
