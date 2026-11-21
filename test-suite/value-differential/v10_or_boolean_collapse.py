"""v10 DISAGREE — the BOOLEAN-COLLAPSE answer 1. CPython says 5. PyCSL must REFUSE."""


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: int = 0
    b: int = 5
    return a or b


if __name__ == "__main__":
    print(f())
