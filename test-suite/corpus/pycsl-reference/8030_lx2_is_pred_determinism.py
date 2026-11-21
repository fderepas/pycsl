r"""Test 8030 -- wall lex-char-class step 3 (expected PASS: UNPROVABLE at base): `c.isdigit()` (named receiver, `py_isdigit_op c`) and `s[i].isdigit()` (computed receiver, formerly the unrelated polymorphic `isdigit_1`) on the SAME value must give the same answer. With the deterministic `py_isdigit_op` (pinned to the logic `py_isdigit_f`) and the computed-receiver arm calling it, the mismatch branch is unreachable and `\result == 0` proves.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires 0 <= i and i < len(s)
#@ ensures \result == 0
#@ assigns \nothing
def mismatch(s: str, i: int) -> int:
    c = s[i]
    if c.isdigit():
        if not s[i].isdigit():
            return 1
    return 0


if __name__ == "__main__":
    for s in ["a1", "12", "x", "٣"]:
        for i in range(len(s)):
            r = mismatch(s, i)
            print("VIOLATION contract" if r != 0 else "result", r)
