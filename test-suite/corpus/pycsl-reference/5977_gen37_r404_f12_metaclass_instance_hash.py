r"""Test 5977 -- gen #37 route #404 (expected FAIL): red team 32 witness `f12_metaclass_instance_hash` -- a file metaclass deriving from `type` defines behaviour the model ignores (PROVED at base 4431ef86f; CPython violates, see the driver). REFUSED (PYCSL-S1-UNMODELLED-BASE: `type` is a modelled base only for a metaclass that defines nothing).
"""
# pycsl-expected: FAIL
class M(type):
    def __eq__(cls, other: object) -> bool:
        return True


class K(metaclass=M):
    def __init__(self) -> None:
        self.x: int = 1


#@ no_exception \all
def f(k: K) -> int:
    s = {type(k)}
    return len(s)


if __name__ == "__main__":
    try:
        r = f(K())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
