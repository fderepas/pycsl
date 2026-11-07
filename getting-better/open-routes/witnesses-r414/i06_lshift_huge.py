#@ requires n >= 0
#@ no_exception \all
def f(n: int) -> int:
    return 1 << n


if __name__ == "__main__":
    try:
        r = f(2**64)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
