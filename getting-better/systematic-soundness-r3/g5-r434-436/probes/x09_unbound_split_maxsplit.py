#@ no_exception \all
def f(s: str, n: int) -> int:
    return len(str.split(s, " ", n))


if __name__ == "__main__":
    try:
        print("result", f("a b", 10**20))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
