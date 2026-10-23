# ROUTE #179 — a raising constructor is lowered as a record literal, and the raise is gone

**Status: CLOSED by gen #29 (battery R green: suite 3761/3779, same 18 CONFIRMED FAIL, zero XPASS; planes --slow 34/34 on a relaunch).** Severity 1.
Generator: hand (raising callees of every call spelling, after #176).

## Measured at `b795f888`

    class C:
        def __init__(self, v: int) -> None:
            if v < 0: raise ValueError()
            self.v = v
    #@ no_exception ValueError
    def probe() -> int:  c = C(-1); return 0                         PROVED  (CPython ValueError)
    #@ ensures \result == 0
    def probe() -> int:
        try: c = C(-1)
        except ValueError: return 9
        return 0                                                     PROVED  (CPython 9)

Same through a dataclass `__post_init__`. Emitted: `let c = { v = (- 1) } in ()` — the construction
synthesis (`construction_synth.py`) builds a record value and never sees the raise. Refused at HEAD:
a raising property getter, a staticmethod via the class, a raising method inside a call argument.

## Repair (draft)

`pycsl.py::_run_pipeline` (trusted), source-level like #175: classes whose `__init__` / `__post_init__`
/ `__new__` (own or inherited) contain a `raise` are collected with the raised names; functions that
construct one directly, or call same-file functions that do (transitively), are refused
(PYCSL-R179) when they declare `no_exception` for the exception (or `\all`) or hold a handler that
catches it. A caller that merely constructs (no claim about the exception) is unaffected: its
postconditions are partial-correctness claims about normal return.

Emission byte-inert (corpus/pyref/mirrors). Witnesses 1630-1632 (XFAIL), 1633 (PASS). Fast planes 19/19
(after inlining a nested helper that moved mirror-coverage), conformance, sync green.
