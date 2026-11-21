#@ no_exception \all
def f(t: tuple) -> int:
    s = {(u := t)}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(([1],))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
