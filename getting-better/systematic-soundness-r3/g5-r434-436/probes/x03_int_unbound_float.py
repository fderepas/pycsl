#@ no_exception \all
def f(x: float) -> int:
    k = int.bit_length(x)
    return 0


if __name__ == "__main__":
    try:
        print("result", f(1.5))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
