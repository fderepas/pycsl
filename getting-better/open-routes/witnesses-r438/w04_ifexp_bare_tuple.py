#@ no_exception \all
def f(t: tuple, c: bool) -> int:
    s = {t if c else ()}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(([1],), True)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
