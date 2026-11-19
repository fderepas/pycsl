def h(s: str) -> int:
    return ord(s)


#@ no_exception \all
def f(s: str) -> int:
    return h(s)


if __name__ == "__main__":
    try:
        print("result", f("ab"))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
