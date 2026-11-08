#@ ensures \result == True
def f(s: str) -> bool:
    t = "é" + s
    return len(t) > 2


if __name__ == "__main__":
    try:
        r = f('a')
        if not (r == True):
            print("VIOLATION ensures", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
