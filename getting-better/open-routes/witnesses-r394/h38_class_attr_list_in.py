class C:
    XS = [1]


#@ no_exception \all
def f(s: dict) -> bool:
    return C.XS in s


if __name__ == "__main__":
    try:
        print("result", f({}))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
