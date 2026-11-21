r"""Test 9599 -- route #590 WITNESS (expected FAIL: REFUSED PYCSL-R590-RAISE-NON-EXCEPTION at HEAD, every model): `raise mk()` raises whatever the FUNCTION `mk` returns (here a ValueError), but the model raised a tag named `mk`, so `except ValueError` was dead in the proof. CPython returns 1; the claim `\result == 0` is false.
"""
# pycsl-expected: FAIL
#@ assigns \nothing
def mk() -> ValueError:
    return ValueError("x")


#@ ensures \result == 0
def f(k: int) -> int:
    try:
        raise mk()
    except ValueError:
        return 1
    return 0


if __name__ == "__main__":
    print(f(0))
