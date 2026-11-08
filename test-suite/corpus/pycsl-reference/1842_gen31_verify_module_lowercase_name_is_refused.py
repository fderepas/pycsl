r"""Test 1842 — gen #31 WITNESS: a lowercase `#@ verify_module` name is REFUSED.

`#@ verify_module <name>` is lowered to a Why3 `module <name>` (plus a synthesized
`<name>Sig` interface module), and Why3 module names must be CAPITALIZED identifiers.
Emitted as written, a lowercase group name produces

    syntax error: expected module name must be an capitalized identifier
    (token UIDENT_NQ), found "leafSig"

— an error naming a symbol that appears NOWHERE in the user's source, because the `Sig`
suffix is synthesized by the emitter. That is the worst shape a diagnostic can take: it
sends the reader to the wrong file. Nothing was unsound (the run failed either way); what
was wrong is which message the user reads.

Refused at `_run_pipeline` with `PYCSL-SEM-VERIFY-MODULE-NAME-NOT-CAPITALIZED`, naming the
directive and the fix. Control: 1843, the same program with the name capitalized, which
verifies.

Found while trying to write this directive's pair for
`bin/check-directive-enforcement.py`. The pair is NOT written — the observable difference
`#@ verify_module` makes is which `#@ proof` axioms co-reside, and those need a Rocq
toolchain this switch does not have — so the directive stays in that plane's UNCOVERED
list with the reason recorded.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ verify_module leafmod
    #@ ensures \result >= 0
    #@ assigns \nothing
    def leaf(self) -> int:
        return 7

    #@ ensures \result >= 0
    #@ assigns \nothing
    def caller(self) -> int:
        return self.leaf()
