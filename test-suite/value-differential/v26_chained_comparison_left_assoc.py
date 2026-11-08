"""v26 DISAGREE — the left-associative `(5 > 3) > 1` reading of a chained comparison. Python gives True (1); this claims the 0 that `1 > 1` would produce."""


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a: int = 5
    b: int = 3
    c: int = 1
    return a > b > c


if __name__ == "__main__":
    print(int(f()))
