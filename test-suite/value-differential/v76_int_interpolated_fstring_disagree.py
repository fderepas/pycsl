"""v76 DISAGREE — `f"{5}"` IS `"5"`, so a model in which it is the integer 5 answers 2 (ROUTE #203)."""


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    n = 5
    s = f"{n}"
    if s == "5":
        return 1
    return 2


if __name__ == "__main__":
    print(f())
