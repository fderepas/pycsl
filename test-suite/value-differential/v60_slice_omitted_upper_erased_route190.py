"""v60 DISAGREE — the ERASED reading of an omitted slice upper bound. Python gives 'bcde' (4); this claims the 0 that a `None`-as-zero upper bound produces. This is route #190 stated as a value claim."""


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    s: str = "abcde"
    return len(s[1:])


if __name__ == "__main__":
    print(f())
