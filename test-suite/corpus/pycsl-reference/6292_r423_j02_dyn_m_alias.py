r"""Test 6292 -- route #423 (expected FAIL): red team 33 witness `j02_dyn_m_alias` (getting-better/open-routes/witnesses-r423/j02_dyn_m_alias.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
class M(type):
    pass


class B(metaclass=M):
    def __init__(self) -> None:
        self.x: int = 1


#@ no_exception \all
def f(b: B) -> int:
    s = {b}
    return len(s)


if __name__ == "__main__":
    MM = M
    D = MM("D", (B,), {"__hash__": None})
    try:
        r = f(D())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
