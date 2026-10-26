#@ requires s == "é"
#@ no_exception \all
def f(s: str) -> str:
    return s[1]


if __name__ == "__main__":
    try:
        r = f('é')
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
