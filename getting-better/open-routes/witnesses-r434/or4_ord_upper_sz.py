#@ no_exception \all
def f(s: str) -> int:
    return ord(s.upper())


if __name__ == "__main__":
    try:
        r = f("\xdf")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
