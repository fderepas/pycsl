#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception ValueError
def f(x: int) -> int:
    s = str(x)
    return 1

if __name__ == "__main__":
    f(10**5000)
