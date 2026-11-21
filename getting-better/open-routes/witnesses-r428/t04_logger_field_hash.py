import logging


class R:
    def __init__(self) -> None:
        self.handlers: int = 0
        logging.Logger.__init__(self, "n")


#@ no_exception \all
def f(r: R) -> int:
    s = {r.handlers}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(R())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
