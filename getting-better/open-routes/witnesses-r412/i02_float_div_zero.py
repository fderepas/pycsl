#@ no_exception \all
def f(x: float, y: float) -> float:
    return x / y


if __name__ == "__main__":
    try:
        r = f(1.0, 0.0)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
