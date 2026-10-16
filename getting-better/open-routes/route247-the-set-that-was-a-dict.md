# OPEN ROUTE #247 — `set` / `frozenset` SHARE `dict`'s TYPE TAG

**Status: OPEN (gen #36, 2026-10-16), Severity 1.** Residual of the #246 repair; driver-verified to PROVE at
the #246 candidate tree (= HEAD 1a86a361).

## Witness
`witnesses-r246/dict_set_tag.py`: `d: Dict[int, int]`, `if isinstance(d, set): return 1` proves
`\result == 1`; CPython `f({})` returns 0.

## Mechanism
The isinstance tag table maps set/frozenset onto dict's tag (all are lowered to maps), so a typed-dict
subject decides `isinstance(d, set)` TRUE.

## Repair direction
Give set/frozenset their own tag (or decide `isinstance(<typed Dict>, set)` FALSE / `isinstance(<typed Set>,
dict)` FALSE from the declared type), opaque where the static type is unknown.
