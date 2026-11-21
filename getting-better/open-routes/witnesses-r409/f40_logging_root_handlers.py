import logging


#@ no_exception \all
def f() -> int:
    s = {logging.root.handlers}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
