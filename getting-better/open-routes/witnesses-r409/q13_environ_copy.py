import os


#@ no_exception \all
def f() -> int:
    s = {os.environ.copy()}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
