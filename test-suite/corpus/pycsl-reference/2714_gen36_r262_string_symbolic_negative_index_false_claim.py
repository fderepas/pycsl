r"""Test 2714 — route #262 (expected FAIL): a contract `s[k]` on a `str` lowered to
`String.substring s k 1`, which Why3 defines as `""` for `k < 0`, so `s[k] == ""` with
`k == -1` PROVED over a length-2 string at b35d9c5e. CPython: "ab"[-1] == "b".
"""
# pycsl-expected: FAIL


#@ requires len(s) == 2 and k == -1
#@ ensures s[k] == ""
#@ assigns \nothing
def f(s: str, k: int) -> int:
    return 0


if __name__ == "__main__":
    assert f("ab", -1) == 0 and "ab"[-1] == "b"
