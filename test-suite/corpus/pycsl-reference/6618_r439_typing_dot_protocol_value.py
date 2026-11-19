r"""Test 6618 -- route #439 (expected FAIL): NEW latent: `{c}` with `c: Pr`, `class Pr(typing.Protocol)` spelled through the module. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R349-UNHASHABLE-RECORD).
"""
# pycsl-expected: FAIL
import typing

class Pr(typing.Protocol):
    def __len__(self) -> int:
        ...


#@ no_exception \all
def f(c: Pr) -> int:
    s = {c}
    return len(s)


if __name__ == "__main__":
    try:
        r = f([1])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
