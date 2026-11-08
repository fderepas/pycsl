r"""Test 3027 — route #276 (expected FAIL): `--strict-latin1` drops LATIN1-STR.

Same program as 3023: the `ord(s[i])` codec form: `requires len(s) >= 1`, `ensures \result < 256` over `return ord(s[0])`. Under the flag `ord` reads an UNINTERPRETED code point
`pycsl_cp s i` clamped to [0, 0x10FFFF] by a definitional `if` (no axiom, not linked to
`Char.code`) and `chr(n)` has code point `n`, so the claim, FALSE in CPython, no longer proves.
"""
# pycsl-flags: --strict-latin1
# pycsl-expected: FAIL


#@ requires len(s) >= 1
#@ ensures \result < 256
#@ assigns \nothing
def f(s: str) -> int:
    return ord(s[0])


if __name__ == "__main__":
    print(f("ab"), f("\u20acb"))  # 97 8364: the claim is FALSE for a leading euro sign
