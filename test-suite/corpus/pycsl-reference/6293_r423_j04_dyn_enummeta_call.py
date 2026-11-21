r"""Test 6293 -- route #423 (expected FAIL): red team 33 witness `j04_dyn_enummeta_call` (getting-better/open-routes/witnesses-r423/j04_dyn_enummeta_call.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
class B:
    def __init__(self) -> None:
        self.x: int = 1


#@ no_exception \all
def f(b: B) -> int:
    s = {b}
    return len(s)


if __name__ == "__main__":
    import enum
    D = enum.EnumMeta("D", (B,), {"__hash__": None}) if False else type.__call__(type, "D", (B,), {"__hash__": None})
    try:
        r = f(D())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
