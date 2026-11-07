r"""Test 2364 — route #247 (expected PASS): CONTROL. In a CONTRACT a subject declared `set` still
DECIDES: `isinstance(x, set)` TRUE, `frozenset` and `dict` FALSE (the new tags' literals are inlined,
`(subtag 7 7)`, `(subtag 7 8)`, no new declaration). CPython `f({1})`: all three hold.
"""
# pycsl-expected: PASS


#@ ensures isinstance(x, set)
#@ ensures not isinstance(x, frozenset)
#@ ensures not isinstance(x, dict)
#@ assigns \nothing
def f(x: set) -> int:
    return 0


if __name__ == "__main__":
    s = {1}
    assert isinstance(s, set) and not isinstance(s, frozenset) and not isinstance(s, dict)
    assert f(s) == 0
