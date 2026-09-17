# ROUTE #175 — a user exception subclass escapes its base-class handler in the proof

**Status: REPAIR DRAFTED by gen #29 (worktree wtV, on top of #174).** Severity 1. Generator: hand
(exception hierarchy probes after #170-#174).

## Measured at `0beed736`

    class MyErr(ValueError): pass
    #@ ensures \result == 0
    def probe() -> int:
        try: raise MyErr()
        except ValueError: return 9
        return 0                               PROVED   (CPython 9)

Same with `class Sub(Base)` / `except Base`. Emitted: `try raise MyErr with ValueError -> ... end`
plus an added `raises { MyErr }` — Why3 exceptions are flat, and handler expansion
(`exception_model.EXCEPTION_BASES`) knows only builtin classes. Refused at HEAD: handler order,
bare re-raise, raise inside a handler, tuple handlers of user classes, a callee `#@ raises Sub`
caught by `except Base` (other pipeline refusal).

## Repair (draft)

`pycsl.py::_run_pipeline` (trusted; the resolved IR has already cleared class `bases` when
inheritance is merged): parse the source, map user classes to their bases, and in every non-trusted
function refuse (PYCSL-R175) a handler naming a STRICT ancestor (user bases, then the builtin MRO) of
an exception raised in its `try` body (a `raise`, or a call to a function whose `#@ raises` names
it). Emission inert (corpus/pyref/mirrors). Witnesses 1608, 1609 (XFAIL), 1610 (PASS: caught by its
own name). Fast planes, conformance, sync green.

## Still open

A user subclass raised by an UNANNOTATED callee (no `#@ raises`) is invisible to the check; the
faithful fix (user classes in the handler expansion) needs `_handle_try_stmt` (verified mirror).
