r"""Test 1603 - ROUTE #174 control (gen #29): a narrow `except OSError` around an EXPLICIT `raise FileNotFoundError()` is still modelled and `\result == 9` proves.
"""
_ = 0  # anchor


#@ requires k >= 0
#@ ensures \result == 9
def probe(k: int) -> int:
    try:
        if k >= 0:
            raise FileNotFoundError()
        return 1
    except OSError:
        return 9
