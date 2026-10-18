# FALSE: a nested class body runs at def time; its statement divides by zero.
#@ requires x == 0
#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def f(x: int) -> int:
    class K:
        v = 10 // x
    return 1

if __name__ == "__main__":
    print(f(0))
