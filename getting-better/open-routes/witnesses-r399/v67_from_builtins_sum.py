from builtins import sum


#@ ensures \result == 3
def f() -> int:
    return sum([1, 2], **{"start": 10})


if __name__ == "__main__":
    try:
        print("result", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
