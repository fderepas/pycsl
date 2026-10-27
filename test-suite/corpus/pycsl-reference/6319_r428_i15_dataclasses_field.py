r"""Test 6319 -- route #428 (expected FAIL): red team 33 witness `i15_dataclasses_field` (getting-better/open-routes/witnesses-r428/i15_dataclasses_field.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
import dataclasses


class R:
    def __init__(self) -> None:
        self.x: int = 1
        dataclasses.Field.__init__(self, 1, 2, True, True, None, True, None, False, None)


#@ ensures \result == 7
def f(r: R) -> int:
    return getattr(r, "default", 7)


if __name__ == "__main__":
    try:
        r = f(R())
        if not (r == 7):
            print("VIOLATION ensures", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
