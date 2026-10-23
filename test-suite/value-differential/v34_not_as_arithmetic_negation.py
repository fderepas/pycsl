"""v34 DISAGREE — the `not` == `nonzero` reading. Python gives 0 for `not 5`; this claims the 1 that reading truthiness the wrong way round would produce."""


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: int = 5
    return not a


if __name__ == "__main__":
    print(int(f()))
