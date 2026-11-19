r"""Test 6322 -- route #428 (expected FAIL): red team 33 witness `t04_logger_field_hash` (getting-better/open-routes/witnesses-r428/t04_logger_field_hash.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
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
