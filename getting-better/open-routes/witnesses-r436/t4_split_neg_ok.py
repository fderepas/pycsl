#@ no_exception \all
def f(s: str, n: int) -> int:
    return len(s.split(" ", n))


if __name__ == "__main__":
    try:
        r = f("a b", -(10**20))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
