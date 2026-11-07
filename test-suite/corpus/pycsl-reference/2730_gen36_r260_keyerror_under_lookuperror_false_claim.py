r"""Test 2730 — route #260 (expected FAIL): `raise KeyError` inside `try` is caught by `except LookupError`
(KeyError <: LookupError), so CPython returns 7. Before the repair the handler matched only the
exact tag `LookupError`, the raise escaped into an added `raises { KeyError }`, and the false
`\result == 0` PROVED vacuously. Now the handler expands to a `KeyError` arm and the claim fails.
"""
# pycsl-expected: FAIL
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    r = 0
    try:
        raise KeyError("k")
    except LookupError:
        r = 7
    return r

if __name__ == "__main__":
    print(f())
