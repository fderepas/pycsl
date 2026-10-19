r"""Test 3025 — route #276 (expected FAIL): `--strict-latin1` drops LATIN1-STR.

Same program as 3021: `ensures \result != 300` over `return ord(chr(300))`. Under the flag `ord` reads an UNINTERPRETED code point
`pycsl_cp s i` clamped to [0, 0x10FFFF] by a definitional `if` (no axiom, not linked to
`Char.code`) and `chr(n)` has code point `n`, so the claim, FALSE in CPython, no longer proves.
"""
# pycsl-flags: --strict-latin1
# pycsl-expected: FAIL


#@ ensures \result != 300
#@ assigns \nothing
def f() -> int:
    return ord(chr(300))


if __name__ == "__main__":
    print(f())  # 300: the claim is FALSE
