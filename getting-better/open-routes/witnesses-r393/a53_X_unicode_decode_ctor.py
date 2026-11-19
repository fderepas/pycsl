class D(UnicodeDecodeError):
    pass


#@ no_exception \all
def f() -> int:
    e = D("x")
    return 1


if __name__ == "__main__":
    try:
        print("no violation", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
