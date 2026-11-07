# FALSE: `case False:` uses `is`; f(0) returns 0 in CPython, claim says 7 for n == 0.
#@ ensures n == 0 ==> \result == 7
#@ assigns \nothing
def f(n: int) -> int:
    match n:
        case False:
            return 7
        case _:
            return 0

if __name__ == "__main__":
    print(f(0))
