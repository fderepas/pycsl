r"""Test 6297 -- route #424 (expected FAIL): red team 33 witness `a10_meta_new_returns_list` (getting-better/open-routes/witnesses-r424/a10_meta_new_returns_list.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
class M(type):
    pass


class K(metaclass=M):
    def __class_getitem__(cls, item: int) -> list:
        return [item]


#@ no_exception \all
def f() -> int:
    s = {K[1]}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
