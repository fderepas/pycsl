# ROUTE #161 — an OPAQUE builtin call is assumed not to raise under `no_exception`

**Status: CLOSED AND FULLY GATED by gen #29 (2026-09-16), battery I (with #162).** Severity 1.

## Measured on the #159/#160 candidate (and at `87258ff7`)

    "{1}".format(0)          #@ no_exception IndexError   PROVED   (CPython IndexError)
    math.factorial(-1)       #@ no_exception ValueError   PROVED   (CPython ValueError)

plus route #160's four (range zero step, split(""), pow(0, -1), max([])) repaired one by one.

## The systemic shape

`no_exception E` injects obligations only at sites that look a TRIGGER row up (binop, subscript,
map_get, chr, del, bytes store) and refuses a hand-written list of orphan calls (routes #65, #66, #72,
#160). Every OTHER builtin or stdlib call lowers to an abstract `val` with no `raises` and is thereby
assumed not to raise — the list of refusals can never be complete.

## Candidate systemic repair (not landed — census first)

Under a `no_exception` context, refuse any call whose callee is neither (a) a function of the
verified program or a stub with its own `raises`/`no_exception` contract, nor (b) on a WHITELIST of
builtins known never to raise the declared exceptions for any argument (e.g. `len`, `abs`, `min`/`max`
of two or more arguments, `sorted`, `bool`, `str` of an int). Census the corpus `no_exception`
functions' callees first and predict the refused set; an honest regression there is the price.

## Draft (wtJ)

In `_reset_function_state` (trusted), after the route #65/#66/#72/#160 refusals: under a
`no_exception` context a Call is allowed only if its callee is a program function / record type (by
name, dotted name, or method tail), or an undotted builtin on a whitelist (len, abs, bool, str, repr,
sorted, reversed, list, tuple, set, frozenset, dict, enumerate, zip, range, min, max, sum, any, all,
isinstance, chr, ord, int, float, print, hash, id, type, iter, map, filter, round, bytearray, bytes,
pow), or a method on a whitelist (append ... bit_length). Every `no_exception` file of both corpora
re-run on the draft: all as expected. Witnesses 1554/1555.

**Battery I (every leg predicted and hit):** emission measured before predicting — the sweep caught a
#162 draft-1 precision regression (14 python-reference stdlib smoke tests GONE), fixed in draft 2;
final emission vs the #158-#160-closed tree: 1196 -> 1195 with exactly ONE intended GONE (0386, an
unresolved callee under `no_exception`), python-reference and mirrors inert; conformance 38/38 + 38/38;
suite 3683/3701 same 18, zero XPASS; planes --slow 34/34.
