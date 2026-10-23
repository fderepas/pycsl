"""v12 DISAGREE — claims the empty string is TRUTHY. CPython says 0. PyCSL must REFUSE."""


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    s: str = ""
    if s:
        return 1
    return 0


if __name__ == "__main__":
    print(f())
