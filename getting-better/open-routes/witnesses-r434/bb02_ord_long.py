#@ no_exception \all
def f(s: str) -> int:
    return ord(s)


if __name__ == "__main__":
    try:
        r = f("ab")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
