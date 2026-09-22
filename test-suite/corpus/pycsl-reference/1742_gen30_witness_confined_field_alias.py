r"""Test 1742 — WITNESS: aliasing a READ-CONFINED field into a local.

`#@ happy ... reading self.secret region 0 .. 4 except reader` confines who may READ the
protected region. A non-exempt method that binds `alias = self.secret` and reads through
the alias would evade the per-read-site check, so the aliasing is refused outright ("read
through self.secret directly, or add the method to `except`").

One of the refusals `bin/check-refusal-witness-coverage.py` measured as having no file
proving it can fire — and one whose absence matters, because the whole read-confinement
form rests on it.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ happy conf:
#@     reading self.secret
#@     region 0 .. 4
#@     except reader
#@ class invariant \length(self.secret) >= 8
class S:
    def __init__(self) -> None:
        self.secret: list = [0] * 8

    #@ assigns \nothing
    def reader(self) -> int:
        return self.secret[0]

    #@ assigns \nothing
    def peeker(self) -> int:
        alias = self.secret
        return alias[0]
