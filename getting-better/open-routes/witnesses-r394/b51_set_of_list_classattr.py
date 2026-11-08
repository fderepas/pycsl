class C:
    XS = [1]


#@ no_exception \all
def f() -> int:
    s = {C.XS}
    return len(s)


if __name__ == "__main__":
    try:
        print("no violation", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
