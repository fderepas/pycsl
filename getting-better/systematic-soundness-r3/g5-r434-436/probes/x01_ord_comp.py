#@ no_exception \all
def f(ws: list[str]) -> int:
    xs = [ord(w) for w in ws]
    return 0


if __name__ == "__main__":
    try:
        print("result", f(["ab"]))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
