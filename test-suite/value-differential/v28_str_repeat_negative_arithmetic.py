"""v28 DISAGREE — the len(s)*n reading of a negative string repeat. Python gives 0; this claims the -6 a model that multiplies the length would produce (and a NEGATIVE length is not even a possible string)."""


#@ ensures \result == -6
#@ assigns \nothing
def f() -> int:
    s: str = "ab"
    return len(s * -3)


if __name__ == "__main__":
    print(f())
