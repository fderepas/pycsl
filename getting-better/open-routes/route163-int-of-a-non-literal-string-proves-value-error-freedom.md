# ROUTE #163 — `int()`/`float()` of a string that is not a literal or a `str`-typed name proves `no_exception ValueError`

**Status: REPAIR DRAFTED by gen #29 (worktree wtK, on top of battery I's candidate).** Severity 1.
Generator: carrier-rerun (route #66's own "is it a string?" test).

## Measured at `7c8f275f`

    int(getname())      # getname() -> str returns "x"     no_exception ValueError   PROVED (CPython raises)
    int(p.s)            # p.s is a string field             no_exception ValueError   PROVED (CPython raises)

Route #66 refused `int(<str>)` only when the argument was a String literal or a Var the symbol table
types `str`; every other string reached the whitelisted `int` and was assumed numeric.

## Repair

Inverted: under `no_exception ValueError`, `int`/`float` need a PROVABLY numeric argument — a numeric
literal or operator result, a name typed int/float/bool, a call to a numeric builtin, or a call to a
program function annotated as returning int/float/bool — or the call is refused. Every
`no_exception` corpus file re-run as expected. Witnesses 1558/1559.
