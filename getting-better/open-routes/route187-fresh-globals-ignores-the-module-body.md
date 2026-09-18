# ROUTE #187 — `#@ fresh_globals` assumes the constructor post-state, and the module body's own mutations are invisible

**Status: CLOSED by gen #29 (battery AA green: suite 3793/3811, the same 18 CONFIRMED FAIL, zero XPASS; planes --slow 34/34; emission byte-inert in all three directions).**
Severity 1.
Generator: hand probe of the opt-in trust surfaces (annotations.md #28).

## Measured at `8a30d42f`

    class Counter:
        #@ assigns self.n
        #@ ensures self.n == 0
        def __init__(self) -> None:  self.n: int = 0

    counter = Counter()
    counter.n = 7                       # <-- the module body runs at import

    #@ ensures \result == 0
    #@ fresh_globals
    def probe() -> int:  return counter.n          PROVED   (CPython 7)

    counter = Counter()
    counter.bump()                      # bump: `ensures self.n == 3`
    ... same driver                                 PROVED   (CPython 3)

`#@ fresh_globals` re-establishes each module-global singleton's `__init__` post-state as an
ASSUMED entry fact. The IR records a global as `{name, class, value}` only — **every other
top-level statement is dropped on the floor** (`module_globals` for the probe above holds just
`{"name": "counter", "class": "Counter", "value": {Call Counter}}`). So the assumed fact describes
the state immediately after construction, while the program has already left it. Without the
directive both probes FAIL (the global is havoc'd), so the assumed fact is the whole gap.

The existing `PYCSL-SEM-FRESH-GLOBALS` confinement checks only that the driver (1) is not a method
and (2) is called by nobody. Neither looks at the module body — the confinement was written about
*who enters the driver*, and the hole is about *what ran before anyone did*.

## Repair

The IR cannot see the statements, so the check reads the SOURCE, like routes #175/#179/#181: with a
`#@ fresh_globals` function in the file, the module body may contain only imports, definitions, a
docstring, and simple `name = <expr>` bindings that neither rebind a name nor read a global
singleton. An attribute/subscript store, a bare call, an `if` or a loop at module level is refused
(`PYCSL-R187-FRESH-GLOBALS-MODULE-BODY`). Fail-closed: a module body the IR does not carry cannot be
shown harmless. Witnesses 1661, 1662 (XFAIL), 1663 (PASS control); corpus 0713 (the only
`fresh_globals` reference test) still proves.
