r"""Test 6321 -- route #428 (expected FAIL): red team 33 witness `t01_userlist_field_hash` (getting-better/open-routes/witnesses-r428/t01_userlist_field_hash.py). PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).
"""
# pycsl-expected: FAIL
import collections


class R:
    def __init__(self) -> None:
        self.data: int = 0
        collections.UserList.__init__(self, [1])


#@ no_exception \all
def f(r: R) -> int:
    s = {r.data}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(R())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
