# ROUTE #164 — an ERASED subscript read on a non-literal mapping proves `no_exception KeyError`

**Status: CLOSED AND FULLY GATED by gen #29 (2026-09-17), battery J (with #163).** Severity 1. Generator: carrier-rerun on
gen #29's own landed route #159.

## Measured at `7c8f275f`

    v = os.environ["<absent key>"]     #@ no_exception KeyError   PROVED   (CPython KeyError)

Route #159 gave an erased `subscript_get` read an unprovable IndexError obligation, and an unprovable
KeyError obligation only when the receiver was a dict LITERAL. Any other erased receiver (a module
attribute mapping, an unmodelled object) may be a mapping too.

## Repair

Every erased `subscript_get` read carries the `assert { false }` KeyError obligation under
`no_exception KeyError` / `\all`. A dict returned by a call and a dict field go through the map path
and were already fail-closed. Witness 1560.

**Battery J (every leg predicted and hit):** emission measured before predicting — vs the
#161/#162-closed tree 1195 -> 1196, 0 MOVED / 0 GONE / 0 APPEARED, python-reference and mirrors
inert; conformance 38/38 + 38/38; suite 3686/3704 same 18, zero XPASS; planes --slow 34/34.
