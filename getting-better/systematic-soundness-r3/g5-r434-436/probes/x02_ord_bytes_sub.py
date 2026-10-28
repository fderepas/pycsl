#@ no_exception \all
#@ requires len(b) >= 1
def f(b: bytes) -> int:
    return ord(b[0])


if __name__ == "__main__":
    try:
        print("result", f(b"a"))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
