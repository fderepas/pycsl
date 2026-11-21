# ROUTE #176 — a stubbed method call never raises, so the caller's handler is dead

**Status: CLOSED by gen #29 (battery P green: suite 3743/3761, same 18 CONFIRMED FAIL, zero XPASS; planes --slow 34/34).** Severity 1. Generator:
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

## Carriers folded in

On the draft, `C().go(-1)` (computed receiver, generic unannotated-call fallback) and a `go` that
raises only through a helper `self.check(v)` still PROVED (CPython 9). Escaping exceptions are now
computed transitively over the file's call graph (by name / method-name suffix, catches inside
callees not subtracted — an over-approximation); the computed-receiver fallback may raise every
NAMED exception the calling function handles when a same-file method of that name exists.
A module function raising through `check(v)` and a global-instance method (inlined) were refused at
HEAD. Witnesses 1615-1616 (XFAIL). Emission inert.
An IMPORTED class method raising ValueError, called as `c.go(-1)` under `except ValueError`, PROVED
at HEAD and is refused by the draft (imported stub bodies are in the IR). Witness 1617 (XFAIL) with
helper `multi_file_lib/r176_raising.py`. Imported module functions (`fgo(-1)`, `helper.fgo(-1)`) were
refused at HEAD.
