r"""Test 5981 -- gen #37 route #404 (expected FAIL): red team 32 witness `j36_metaclass_eq_tuple_hash` -- a file metaclass deriving from `type` defines behaviour the model ignores (PROVED at base 4431ef86f; CPython violates, see the driver). REFUSED (PYCSL-S1-UNMODELLED-BASE: `type` is a modelled base only for a metaclass that defines nothing).
"""
# pycsl-expected: FAIL
class M(type):
    def __eq__(cls, other: object) -> bool:
        return True


class C(metaclass=M):
    pass


#@ no_exception \all
def f() -> int:
    s = {(C, 1)}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
