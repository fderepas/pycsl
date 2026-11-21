"""v74 DISAGREE — the EMPTY f-string `f""` is the empty string, not the integer 0 (ROUTE #199)."""


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    s = f""
    if s == "":
        return 1
    return 2


if __name__ == "__main__":
    print(f())
