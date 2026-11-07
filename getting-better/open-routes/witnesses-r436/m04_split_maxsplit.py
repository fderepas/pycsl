#@ no_exception \all
def f(n: int) -> int:
    return len('a b'.split(' ', n))


if __name__ == "__main__":
    try:
        r = f(10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
