"""Test 0978 — a statement-level `#@` directive at COLUMN 0 with nothing after it is
REFUSED; the end-of-file exemption only holds when the block is INDENTED.

`Module3_Weaver.process` has refused an at-EOF `#@` block since #33, but it EXEMPTS the
statement-level directives (`assert`, `assume`, `ghost`, `loop …`, `label`, `reveal`,
`unfold`, `havoc`) on the grounds that "a trailing `#@ assert` IS the last statement of a
body". That is true only INSIDE a body. At column 0 there is no enclosing block:
`Module1_Ingestor._Harvester._assign` takes its `elif nxt is None: pass` branch —
"module-level trailing comment (indent 0) -> ignored, as libcst" — and the directive is
discarded. Measured, before this refusal:

    #@ ensures \result == 0
    def f() -> int:
        return 0
    #@ assert 1 == 2                           <-- FALSE, AND NEVER CHECKED

    [+] Verification SUCCESS! All contracts formally proven.

The same held for a column-0 trailing `#@ ghost`.

The exemption is now conditioned on the block being indented, which is exactly the case it
was written for. CENSUS: 0 column-0 at-EOF statement-level blocks in `pycsl-reference`,
`python-reference`, the mirror, `src/pycsl_lib`, the live emitter and `tests/` — and the
corpus emission is BYTE-IDENTICAL across all 819 files, so the refusal is completely inert.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    return 0
#@ assert 1 == 2
