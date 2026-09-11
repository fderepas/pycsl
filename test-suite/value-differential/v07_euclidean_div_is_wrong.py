"""v07 DISAGREE — the EUCLIDEAN answer -3. CPython says -4. PyCSL must REFUSE."""


#@ ensures \result == -3
#@ assigns \nothing
def f() -> int:
    a: int = 7
    b: int = -2
    return a // b


if __name__ == "__main__":
    print(f())
