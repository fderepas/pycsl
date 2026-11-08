r"""Test 2722 — route #262 COVERAGE (expected PASS; FAILED at b35d9c5e): `s[k]` with
`k == -1` on a length-2 string is `s[1]` — the TRUE claim now proves.
"""


#@ requires len(s) == 2 and k == -1
#@ ensures s[k] == s[1]
#@ assigns \nothing
def f(s: str, k: int) -> int:
    return 0


if __name__ == "__main__":
    assert f("ab", -1) == 0 and "ab"[-1] == "ab"[1]
