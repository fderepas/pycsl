# FALSE: `case True:` compares by IDENTITY (PEP 634); 1 is not True, so the arm is skipped.
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    x = 1
    match x:
        case True:
            return 1
        case _:
            return 0

if __name__ == "__main__":
    print(f())
