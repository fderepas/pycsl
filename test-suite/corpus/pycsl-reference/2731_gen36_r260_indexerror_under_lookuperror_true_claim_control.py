r"""Test 2731 — route #260 CONTROL (expected PASS): `raise IndexError` under `except LookupError`;
CPython returns 7 and the TRUE `\result == 7` proves — now through the handler arm, no longer
vacuously through an escaping raise.
"""
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    r = 0
    try:
        raise IndexError("i")
    except LookupError:
        r = 7
    return r

if __name__ == "__main__":
    print(f())
