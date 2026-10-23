"""v08 DISAGREE — the EUCLIDEAN answer 1. CPython says -1. PyCSL must REFUSE."""


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: int = 7
    b: int = -2
    return a % b


if __name__ == "__main__":
    print(f())
