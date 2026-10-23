r"""Test 1608 - ROUTE #175 (gen #29): `class MyErr(ValueError)`; `try: raise MyErr() except ValueError: return 9; return 0` PROVED `\result == 0` (CPython 9): handler matching knows only the builtin hierarchy, so the raise escaped the handler in the proof. A handler naming a strict ancestor of a raised user exception is now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class MyErr(ValueError):
    pass


#@ ensures \result == 0
def probe() -> int:
    try:
        raise MyErr()
    except ValueError:
        return 9
    return 0
