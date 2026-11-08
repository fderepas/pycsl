"""Test 0093 — Python Reference 3.3.9: With Statement Context Managers"""
# pycsl-expected: FAIL
# (#43) route #20: `with ... as <name>` is REFUSED — `_py_stmt_with` reads only the
# `with` BODY, so the context-manager expression and the binding were both DROPPED and
# the body ran against the PRE-`with` value of the name. Measured: `v = 0;
# with CM() as v: return v` proved `\result == 0` while Python returns 7. This file
# exercises the Python-reference SYNTAX, so the refusal is the honest verdict for it —
# the same treatment #34 gave `python-reference/0111` for `except*`.
_ = 0  # anchor
#@ ensures \result == 0
def test_with_statement_context() -> int:
    """__enter__ and __exit__ for context managers."""
    class CM:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
    with CM() as c:
        pass
    return 0

if __name__ == "__main__":
    assert test_with_statement_context() == 0
