"""v09 DISAGREE — the EUCLIDEAN answer 4. CPython says 3. PyCSL must REFUSE."""


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    a: int = -7
    b: int = -2
    return a // b


if __name__ == "__main__":
    print(f())
