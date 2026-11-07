r"""Test 6320 -- route #428 (expected FAIL): red team 33 witness `i21_string_template` (getting-better/open-routes/witnesses-r428/i21_string_template.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
import string


class R:
    def __init__(self) -> None:
        self.x: int = 1
        string.Template.__init__(self, "a")


#@ ensures \result == 7
def f(r: R) -> int:
    return getattr(r, "template", 7)


if __name__ == "__main__":
    try:
        r = f(R())
        if not (r == 7):
            print("VIOLATION ensures", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
