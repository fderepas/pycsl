#@ no_exception \all
def f(s: set) -> int:
    for x in (y for y in s):
        s.add(x + 100)
    return 0


if __name__ == "__main__":
    try:
        r = f({1})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
