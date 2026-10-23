"""v30 DISAGREE — the unclamped `j - i` reading of a slice length. Python clamps to 4; this claims the 99 that 100-1 would produce."""


#@ ensures \result == 99
#@ assigns \nothing
def f() -> int:
    s: str = "abcde"
    return len(s[1:100])


if __name__ == "__main__":
    print(f())
