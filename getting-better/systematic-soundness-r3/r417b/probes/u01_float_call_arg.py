#@ ensures \result == n
#@ no_exception \all
def g(n: int) -> int:
    return n


#@ no_exception \all
def f(n: int) -> int:
    x = float(g(n))
    return 0


if __name__ == "__main__":
    try:
        print(f(10**400))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
