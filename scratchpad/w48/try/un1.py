#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    n: str = "\N{LATIN SMALL LETTER A}"
    if n == "a" and len(n) == 1:
        return 0
    return 1
