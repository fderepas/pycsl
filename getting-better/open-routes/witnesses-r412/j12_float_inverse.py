#@ requires x > 0.0
#@ no_exception \all
def f(x: float) -> float:
    return 1.0 / (x - x)


if __name__ == "__main__":
    try:
        r = f(1.0)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
