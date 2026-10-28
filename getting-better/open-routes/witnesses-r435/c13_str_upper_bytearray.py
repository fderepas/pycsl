#@ no_exception \all
def f(x: bytearray) -> int:
    s = str.upper(x)
    return 0


if __name__ == "__main__":
    try:
        r = f(bytearray(b"a"))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
