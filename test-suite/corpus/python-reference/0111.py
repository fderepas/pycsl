"""Test 0111 — Python Reference 4.4.2: Python Runtime Model"""
# pycsl-expected: FAIL
# (#34) `except*` is now REFUSED: `_PY_STMT_HANDLERS` has no `TryStar` entry and
# `_py_stmts_to_ir` fell through with no `else`, so the whole statement — the
# `raise` included — was silently DROPPED and `ensures \result == 0` was proved
# by ERASURE. See `frontend/desugar.py::reject_unmodelled` and 0973.
_ = 0  # anchor
#@ ensures \result == 0
def test_exception_groups() -> int:
    """ExceptionGroup bundles multiple exceptions."""
    try:
        raise ExceptionGroup("eg", [ValueError(1), TypeError(2)])
    except* ValueError:
        pass
    except* TypeError:
        pass
    return 0

if __name__ == "__main__":
    assert test_exception_groups() == 0
