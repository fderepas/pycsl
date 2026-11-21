# ROUTE #163 — `int()`/`float()` of a string that is not a literal or a `str`-typed name proves `no_exception ValueError`

**Status: CLOSED AND FULLY GATED by gen #29 (2026-09-17), battery J (with #164).** Severity 1.
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

**Battery J (every leg predicted and hit):** emission measured before predicting — vs the
#161/#162-closed tree 1195 -> 1196, 0 MOVED / 0 GONE / 0 APPEARED, python-reference and mirrors
inert; conformance 38/38 + 38/38; suite 3686/3704 same 18, zero XPASS; planes --slow 34/34.
