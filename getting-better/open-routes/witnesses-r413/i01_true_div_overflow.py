#@ requires b != 0
#@ no_exception \all
def f(a: int, b: int) -> float:
    return a / b


if __name__ == "__main__":
    try:
        r = f(10**400, 1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
