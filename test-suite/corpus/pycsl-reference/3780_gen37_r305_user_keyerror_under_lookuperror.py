r"""Test 3780 -- gen #37 route #305 (expected FAIL): a user `class KeyError(Exception)` (NOT a LookupError) raised inside `try ... except LookupError` under `no_exception \all` + `\result == 1`. Handler matching read the BUILTIN KeyError hierarchy by name and the WhyML tag was the bare name, so the raise was "caught" and the file PROVED while CPython escapes; a user class named like a builtin exception is now refused (PYCSL-R305-BUILTIN-EXCEPTION-NAME-SHADOWED).
"""
# pycsl-expected: FAIL
class KeyError(Exception):
    pass

#@ no_exception \all
#@ ensures \result == 1
def g(x: int) -> int:
    try:
        if x < 0:
            raise KeyError("x")
    except LookupError:
        return 1
    return 1

if __name__ == "__main__":
    assert g(-1) == 1
