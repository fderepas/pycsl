r"""Test 6018 -- gen #37 route #404 (expected FAIL): NEW latent: `M2(M)` with `M(type)` empty and `M2` binding `__eq__`, `class K(metaclass=M2)`, then `{K}` under `no_exception \all` (CPython TypeError). REFUSED (PYCSL-S1-UNMODELLED-BASE: a class deriving from `type` through file classes must define nothing).
"""
# pycsl-expected: FAIL
class M(type):
    pass


class M2(M):
    def __eq__(cls, other: object) -> bool:
        return True


class K(metaclass=M2):
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
