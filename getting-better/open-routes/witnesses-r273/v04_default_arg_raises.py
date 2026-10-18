# FALSE: nested def's default `10 // x` is evaluated when the def runs; x == 0 raises ZeroDivisionError.
#@ requires x == 0
#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def f(x: int) -> int:
    def inner(y: int = 10 // x) -> int:
        return y
    return 1

if __name__ == "__main__":
    print(f(0))
