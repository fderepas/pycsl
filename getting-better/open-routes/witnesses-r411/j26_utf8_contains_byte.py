#@ requires s == "é"
#@ ensures \result == True
def f(s: str) -> bool:
    return len(s) > 1


if __name__ == "__main__":
    try:
        r = f('é')
        if not (r == True):
            print("VIOLATION ensures", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
