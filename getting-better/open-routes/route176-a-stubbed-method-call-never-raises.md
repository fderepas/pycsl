# ROUTE #176 — a stubbed method call never raises, so the caller's handler is dead

**Status: REPAIR DRAFTED by gen #29 (worktree wtW, on top of #175).** Severity 1. Generator:
carrier-rerun of #175 (a raising callee, then the builtin-class case).

## Measured at `3da76330`

    class C:
        def go(self, v: int) -> int:
            if v < 0: raise ValueError()
            return v
    #@ ensures \result == 0
    def probe() -> int:
        c = C()
        try: c.go(-1)
        except ValueError: return 9
        return 0                              PROVED   (CPython 9)

Same via a sibling `self.go(-1)`. The method's own `let` declares `raises { ValueError }`, but the
call lowers to `val c_go_1 (x0: int) : int` with no `raises` (route #167's stub family), so the
handler path is dead. The module-function spelling `go(-1)` is refused (control).

## Repair (draft)

`_handle_dotted_call` (trusted), on the abstract-op fallback: with the callee resolved as in #167,
collect the exceptions it can let escape (declared `raises` plus `IRScanner.collect_escaping_exceptions`
of its body); for each one a handler of the CALLING function catches (`handler_catches`, or a broad
handler), prefix the call with `if (any bool) then raise E;`. The handler path becomes live; an
uncaught escape is refused by Why3. Also: route #175's source check now reads an unannotated callee's
own `raise` statements (a method raising `MyErr(ValueError)` with no `#@ raises`, caught by `except
ValueError`, PROVED). Emission inert (corpus/pyref/mirrors). Witnesses 1611, 1612, 1613 (XFAIL),
1614 (PASS). Fast planes, conformance, sync green.
