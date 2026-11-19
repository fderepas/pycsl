"""v33 AGREE — `not` on a NON-ZERO int is False (0). `not` is defined by TRUTHINESS, not by bitwise or arithmetic negation, so `not 5` is not -6 and not -5."""


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a: int = 5
    return not a


if __name__ == "__main__":
    print(int(f()))
