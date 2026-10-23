"""Test 0979 — a `#@` directive written INSIDE THE CONTINUATION LINES of a simple
statement is REFUSED. It used to be silently discarded while the run reported success.

`Module1_Ingestor._Harvester._assign` associates a `#@` comment with a target by `bisect`
over the targets' START lines. A comment sitting between a leaf statement's FIRST and LAST
line therefore bisects PAST that statement. When the statement is the last one in the file
there is no `nxt` at all, so the comment falls into `elif nxt is None: pass`
("module-level trailing comment -> ignored, as libcst") or, when indented, into
`prev.footer`, which has no lowering for it in this position. Either way it vanishes.

#33's and #34's END-OF-FILE guards in `Module3_Weaver.process` cannot see this shape: the
block does NOT run to end-of-file — the statement's own continuation lines follow it.

Measured, before this refusal:

    #@ ensures \result == 2
    def f() -> int:
        return (
    #@ assert 1 == 2                  <-- FALSE, AND NEVER CHECKED
            2)

    [+] Verification SUCCESS! All contracts formally proven.

The indented form of the same file, the module-level `y: int = (` form of both, and a
`#@ ghost x = 99` + `#@ assert x == 99` PAIR in that position all proved as well.

CENSUS 0 — and the census had to TOKENIZE. A line-based scan of the 3663 annotated files
under `src/`, `test-suite/`, `bin/` and `tests/` reports 95 hits, every one of them `#@`
text inside a DOCSTRING (including the doc-comments of the earlier routes' own witness
tests). Keeping only real COMMENT tokens gives 0, so the refusal is byte-inert; a refusal
built on the line-based number would have rejected 95 innocent files.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL


#@ requires True
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    return (
#@ assert 1 == 2
        2)
