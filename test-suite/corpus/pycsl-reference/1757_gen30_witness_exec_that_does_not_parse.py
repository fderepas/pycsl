r"""Test 1757 — WITNESS: a constant `exec(...)` whose literal is not Python.

The splice parses the literal; a parse failure is a hard error rather than a silently
skipped statement, because skipping it would verify a program with a statement the model
never saw. Sibling of 1756.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 1
def f() -> int:
    exec("this is not python !!")
    return 1
