# ROUTE #161 — an OPAQUE builtin call is assumed not to raise under `no_exception`

**Status: OPEN. Found by gen #29 (2026-09-16), carrier-rerun on its own #160 draft.** Severity 1.

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
