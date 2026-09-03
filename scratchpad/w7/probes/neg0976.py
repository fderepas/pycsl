"""Test 0976 — a `#@` directive above an `if` / `try` / `match`, and one written under a
decorator, are now ATTACHED instead of silently discarded.

`Module1_Ingestor._Harvester._make` returned `mk(None, None)` for `If`, `Try`, `TryStar`
and `Match`, and `_emit_target` emits nothing when `node_type is None`. Every `#@` written
directly above one of those four was therefore discarded BEFORE Module 2 ever parsed it —
and the run still printed *All contracts formally proven*:

    #@ ensures \result == 0
    def f() -> int:
        x: int = 1
        #@ assert 1 == 2                   <-- FALSE, AND NEVER CHECKED
        if True:
            pass
        return 0
    [+] Verification SUCCESS! All contracts formally proven.

Those four are not function/loop/class anchors, but they ARE statements, and the whole
statement-level path was already in place for them: `_attach_labels_and_ghost_assigns`
attaches `label`/`assert`/`check`/`ghost` to any `ast.stmt` by line number, and
`_py_stmts_to_ir` HAS handlers for `If`, `Try` and `Match`. The drop was pure loss.

A `#@` block between a decorator and its `def` was likewise dropped ("invisible to libcst's
leading_lines"); libcst has not been the parser for some time. It is now attached to the
DECORATED function — deliberately, and not by letting it fall through to the generic
branch, which would have handed it to the NEXT definition, a silent MIS-attachment.

LIVE VICTIMS: two `#@ assert self.i > \old(self.i)` in the mirror's own
`pure_ast._Parser.import_from` (2 of 6 staged monotonicity checkpoints, in a file proved at
3103 goals); four `#@ assert` in `src/pycsl_lib`; the mirror's
`Module6_WhyMLTranspiler._heap_var` contract under its `@property`; and `#@ ghost total +=
1` in corpus 0208, which is exactly why that test was `pycsl-expected: FAIL` and now
proves.

Every directive below is a REAL obligation: the run only succeeds because each one is
discharged.
"""


def _identity(fn):
    return fn


#@ requires 0 <= n and n <= 10
#@ ensures \result == n
#@ assigns \nothing
def before_if(n: int) -> int:
    m: int = n
    #@ assert 0 <= m and m <= 3
    if m > 100:
        m = 0
    return m


#@ requires 0 <= n and n <= 10
#@ ensures \result >= 0
#@ assigns \nothing
def before_try(n: int) -> int:
    m: int = n
    #@ assert m >= 0
    try:
        m = m + 1
    except ValueError:
        m = 0
    return m


@_identity
#@ requires 0 <= n and n <= 10
#@ ensures \result == n + 1
#@ assigns \nothing
def under_decorator(n: int) -> int:
    return n + 1
