"""v38 DISAGREE — the right-associative `7 // (2 // 2)` reading. Python gives 1; this claims the 7 that reading would produce."""


#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    return 7 // 2 // 2


if __name__ == "__main__":
    print(f())
