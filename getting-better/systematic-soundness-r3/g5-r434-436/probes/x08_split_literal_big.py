#@ no_exception \all
def f(s: str) -> int:
    return len(s.split(" ", 100000000000000000000))


if __name__ == "__main__":
    try:
        print("result", f("a b"))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
