# FALSE: nested def default raises ValueError via a raising helper; handler path returns 2, claim 1.
#@ ensures \result == 1
#@ assigns \nothing
#@ raises ValueError
def boom() -> int:
    raise ValueError("x")

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    try:
        def inner(y: int = boom()) -> int:
            return y
    except ValueError:
        return 2
    return 1

if __name__ == "__main__":
    print(f())
