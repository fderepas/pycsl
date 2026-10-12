r"""Test 1940 — gen #36 (expected FAIL): ROUTE #231 — return f"{s!r}" is not s (repr adds quotes)

The f-string that forgot its format spec: Module 5 dropped `FormattedValue.format_spec` and
`.conversion`, so `f"{v!c:spec}"` lowered exactly like `f"{v}"`. At 3ca32b8d the FAIL
witnesses of this family PROVED a contract CPython refutes. Here the single-part f-string
lowered to the identity `s`, so `\result == s` PROVED; CPython: f("x") == "'x'".
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == s
#@ assigns \nothing
def f(s: str) -> str:
    return f"{s!r}"
