# OPEN ROUTE #262 — A SYMBOLIC NEGATIVE INDEX IN A CONTRACT READS CELL -1 OF THE LOGICAL ARRAY

**Status: OPEN (gen #36, 2026-10-17), Severity 1.** Red-team round 2; driver-reproduced at HEAD e152fa15 (rc=0).
`witnesses-r262/F5_contract_symbolic_negindex.py`: `requires len(xs) == 2 and k == -1`, `requires xs[1] == 0`,
`ensures xs[k] == \old(xs[k])`, `assigns xs[1]`, body `xs[1] = 7` PROVES (CPython: xs[-1] goes 0 -> 7).
A literal `xs[-1]` is rewritten to `xs[length-1]`; a symbolic `xs[k]` lowers to raw `xs[k]`.
Repair: contract-side `xs[e]` with a possibly-negative `e` lowers to `xs[if e < 0 then length xs + e else e]` (or
requires `e >= 0` / refuses); check body-side symbolic negative indexing too.
