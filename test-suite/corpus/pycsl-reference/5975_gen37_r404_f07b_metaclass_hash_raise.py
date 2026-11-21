r"""Test 5975 -- gen #37 route #404 (expected FAIL): red team 32 witness `f07b_metaclass_hash_raise` -- a file metaclass deriving from `type` defines behaviour the model ignores (PROVED at base 4431ef86f; CPython violates, see the driver). REFUSED (PYCSL-S1-UNMODELLED-BASE: `type` is a modelled base only for a metaclass that defines nothing).
"""
# pycsl-expected: FAIL
class M(type):
    def __hash__(cls) -> int:
        n = len(cls.__name__)
        if n > 0:
            raise ValueError("mh")
        return n


class K(metaclass=M):
    pass


#@ no_exception \all
def f() -> int:
    s = {K}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
