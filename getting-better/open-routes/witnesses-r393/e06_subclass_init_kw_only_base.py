class D(SyntaxError):
    pass


#@ no_exception \all
def f() -> int:
    e = D("m", 1)
    return 1


if __name__ == "__main__":
    try:
        print("result", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
