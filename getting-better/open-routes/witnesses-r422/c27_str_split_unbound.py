#@ no_exception \all
def f() -> int:
    k = str.split('a b')
    s = {k}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
