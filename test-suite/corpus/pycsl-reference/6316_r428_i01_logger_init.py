r"""Test 6316 -- route #428 (expected FAIL): red team 33 witness `i01_logger_init` (getting-better/open-routes/witnesses-r428/i01_logger_init.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
import logging


class R:
    def __init__(self) -> None:
        self.x: int = 1
        logging.Logger.__init__(self, "n")


#@ ensures \result == 7
def f(r: R) -> int:
    return getattr(r, "level", 7)


if __name__ == "__main__":
    try:
        r = f(R())
        if not (r == 7):
            print("VIOLATION ensures", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
