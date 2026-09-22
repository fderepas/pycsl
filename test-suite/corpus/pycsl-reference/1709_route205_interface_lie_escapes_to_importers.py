r"""Test 1709 — ROUTE #205: the narrowing VC was emitted in the OWNING unit only, and the
owning unit is not where the lie is believed.

`_emit_narrowing_vc`'s header says "Emitted only in the owning unit (where the function is
a real `let`, so the definition is established by the body)". An IMPORTER emits the callee
as `val <f> () : int ensures { <the INTERFACE clause> }` and emitted no goal at all, so an
interface that claims MORE than its definition proves was refused at home and believed
everywhere else.

MEASURED: this module FAILS on its own (the narrowing goal `\result == 3 -> \result == 7`
is false), and an importer of it —

    from lie import three
    #@ ensures \result == 7
    def ask() -> int:
        return three()

— PROVED `\result == 7`, with AND without `--deep`, while CPython answers 3. The fix emits
the same goal in the importing unit: it needs no body, because it proves the interface
follows from the DEFINITION CONTRACT, which the owning unit separately proves of its body.
Control: 1710, and corpus 0660 (an honest narrowing) still proves.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ assigns \nothing
#@ ensures \result == 3
#@ interface ensures \result == 7
def three() -> int:
    return 3
