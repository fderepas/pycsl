import logging


class R:
    def __init__(self) -> None:
        self.x: int = 1
        logging.LogRecord.__init__(self, "n", 1, "p", 1, "m", None, None)


#@ ensures \result == 7
def f(r: R) -> int:
    return getattr(r, "msg", 7)


if __name__ == "__main__":
    try:
        r = f(R())
        if not (r == 7):
            print("VIOLATION ensures", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
