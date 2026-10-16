# OPEN ROUTE #247 — `set` / `frozenset` SHARE `dict`'s TYPE TAG

**Status: REPAIRED (gen #36, 2026-10-16; opened the same day), Severity 1.** Residual of the #246 repair; driver-verified to PROVE at
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

## Repair landed (gen #36, 2026-10-16) -- jointly with #248
`expressions._handle_isinstance` + the `_METATYPE_TAGS`/`_TAG_LITERAL` tables (inline; `_handle_isinstance`'s mirror
twin is `\trusted`; the mirror's `_METATYPE_TAGS` copy is updated to the live value, emission-inert).
The general shape is "a tag read off a DECLARED type decides by tag equality where the tag does not name one class
exclusive of every other tested class". Measured instances (all PROVED at afe28c69): `Dict` vs `set` (2340, 2341),
`set` vs `frozenset` (2342), the #246 identity key with the shared literal (2343), two record classes sharing
`tag_record` (declared 2344, `Any` key 2345), `Optional[str]` (a `_union_*` variant) deciding `str` FALSE (2346), a
subject declared `object` deciding `int` FALSE (2347), a subject declared `float` deciding `int` FALSE although PEP 484
admits an `int` actual (2348). Rule:
- `set` -> literal 7, `frozenset` -> literal 8 (builtin tags are pairwise exclusive: their layouts conflict).
  No new declaration: the contract form inlines the literal (`(subtag 7 8)`), the program form already did.
- A declared subject decides only if its tag names one class: a subject declared `object` or `float`, or a
  record/variant tag on EITHER side (shared by many classes, co-subclassable with each other and with builtins),
  is UNDECIDED unless it is the SAME declared class (TRUE). Undecided takes the #246 arm (contract REFUSED,
  program keyed on an unrebound parameter's identity, else `(any bool)`); a record/variant key also names the class.
- The #240 bool arm also treats `float`/`object`/variant subjects as not excluding a bool.
Controls PASS after: 2360 (`Dict` decides dict TRUE / set FALSE), 2361 (same record class TRUE), 2362 (`Any` key:
set and dict exclusive), 2364 (`set` contract: set TRUE, frozenset/dict FALSE). 2360/2362/2364 FAILED at base
(the defect refuted them). Gates and logs: see route #248's section.
