#@ no_exception \all
def f(d: dict) -> int:
    for k in (x for x in d.keys()):
        d[k + 100] = 0
    return 0


if __name__ == "__main__":
    try:
        r = f({1: 1})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
