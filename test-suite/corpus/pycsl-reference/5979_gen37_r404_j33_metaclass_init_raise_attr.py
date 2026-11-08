r"""Test 5979 -- gen #37 route #404 (expected FAIL): red team 32 witness `j33_metaclass_init_raise_attr` -- a file metaclass deriving from `type` defines behaviour the model ignores (PROVED at base 4431ef86f; CPython violates, see the driver). REFUSED (PYCSL-S1-UNMODELLED-BASE: `type` is a modelled base only for a metaclass that defines nothing).
"""
# pycsl-expected: FAIL
class M(type):
    def __init__(cls, name: str, bases: tuple, ns: dict) -> None:
        super().__init__(name, bases, ns)
        cls.K = [1]


class C(metaclass=M):
    K = 1


#@ no_exception \all
def f() -> int:
    s = {C.K}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
