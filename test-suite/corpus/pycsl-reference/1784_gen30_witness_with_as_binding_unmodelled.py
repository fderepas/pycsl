r"""Test 1784 — WITNESS: `with ... as <name>`, whose binding the lowering DROPS.

`_py_stmt_with` reads only the `with` BODY: the context-manager expression and the `as`
binding are both dropped, so the body would run against the PRE-`with` value of the name
while the run still reported "All contracts formally proven". Measured in the refusal's own
comment: `v = 0; with CM() as v: return v` proved `\result == 0` while Python returns 7.
Refused. One of the refusals `bin/check-refusal-witness-coverage.py` measured as having no
witness.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class CM:
    def __init__(self) -> None:
        self.v: int = 7

    #@ ensures \result >= 0
    def __enter__(self) -> int:
        return self.v

    #@ assigns \nothing
    def __exit__(self, a: int, b: int, c: int) -> None:
        return


#@ ensures \result == 0
def read() -> int:
    v = 0
    with CM() as v:
        return v
    return v
