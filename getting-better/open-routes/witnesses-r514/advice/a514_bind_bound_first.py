# advice of PYCSL-R507 (route #514 branch) applied to 8190 (`r = range(n); v = len(r)`): the length taken of `range(..)` spelled in a plain statement, bound stated
#@ requires 0 <= n and n <= 1000
#@ no_exception \all
#@ ensures \result == 1
def f(n: int) -> int:
    v = len(range(n))
    return 1


if __name__ == "__main__":
    print("result", f(5))
