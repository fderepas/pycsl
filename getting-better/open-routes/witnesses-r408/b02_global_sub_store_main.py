XS = [1, 2]


#@ no_exception \all
def f() -> int:
    s = {XS[0]}
    return len(s)


if __name__ == "__main__":
    XS[0] = [5]
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
