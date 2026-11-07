#@ no_exception \all
def f() -> str:
    t = "é"
    return t[1]


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
