# ROUTE #168 — the global-method inliner throws away a discarded tail `return` expression

**Status: REPAIR DRAFTED by gen #29 (worktree wtO, on top of #167).** Severity 1. Generator:
carrier-rerun of #167 (a module-global receiver).

## Measured at `ef82cdc7`

    class C:
        #@ requires self.x != 0
        #@ ensures \result == 1
        def sget(self) -> int: return self.x // self.x
    _g = C(0)
    #@ ensures \result == 5
    def probe() -> int:  _g.sget(); return 5          PROVED   (CPython ZeroDivisionError)

    def run(self) -> int: return self.bumpret()      # bumpret mutates self.x
    #@ ensures \result == 0
    def probe() -> int:  a = _g.x; _g.run(); return _g.x - a     PROVED   (CPython 1)

Emitted `probe` bodies were literally `5` and `a := _g.x; (_g.x - !a)`: `frontend/ir_inline.py`
`_Inliner._expand` pops the callee's tail `return <e>` and, in statement position
(`result_var is None`), drops `<e>` — its evaluation (division check, nested global calls with
their mutations) vanished. Calls on module-global instances are inlined, so route #167's call-site
assertion never sees them either.

## Repair (draft)

In `_expand`, a statement-position tail `return <e>` with a non-None value binds `<e>` to a fresh
`_inl_discard__inlN` local; the fixpoint loop inlines any global call inside it and Module 6 lowers
the evaluation with its checks. Emission: corpus/pyref/mirrors byte-inert apart from the new
witnesses. Witnesses 1575, 1576 (XFAIL), 1577 (PASS control, FAILS at HEAD).

## Still to measure

Other inliner shapes: a callee's `requires` is not checked at an inlined call (only matters when
its violation raises, which the inlined body then checks); a `\trusted` callee is spliced (#106
note) — faithful to CPython, recorded only.
