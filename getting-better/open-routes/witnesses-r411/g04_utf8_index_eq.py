#@ ensures \result == False
def f() -> bool:
    t = "é"
    return t[0] == "é"


if __name__ == "__main__":
    try:
        r = f()
        if not (r == False):
            print("VIOLATION ensures", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
