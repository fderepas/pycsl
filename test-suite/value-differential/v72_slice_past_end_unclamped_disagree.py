"""v72 DISAGREE — the `hi - lo` reading of a past-the-end slice. Python gives '' (0); this claims the 2 that 7-5 would produce."""


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    s: str = "abc"
    return len(s[5:7])


if __name__ == "__main__":
    print(f())
