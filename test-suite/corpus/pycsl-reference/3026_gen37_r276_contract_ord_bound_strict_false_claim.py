r"""Test 3026 — route #276 (expected FAIL): `--strict-latin1` drops LATIN1-STR.

Same program as 3022: a CONTRACT-side `ord`: `requires len(s) == 1`, `ensures ord(s) < 256` (body inert). Under the flag `ord` reads an UNINTERPRETED code point
`pycsl_cp s i` clamped to [0, 0x10FFFF] by a definitional `if` (no axiom, not linked to
`Char.code`) and `chr(n)` has code point `n`, so the claim, FALSE in CPython, no longer proves.
"""
# pycsl-flags: --strict-latin1
# pycsl-expected: FAIL


#@ requires len(s) == 1
#@ ensures ord(s) < 256
#@ assigns \nothing
def f(s: str) -> int:
    return 0


if __name__ == "__main__":
    s = "\u20ac"
    print(f(s), ord(s) < 256)  # 0 False: the postcondition is FALSE for the euro sign
