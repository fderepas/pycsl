# OPEN ROUTE #456 — set-method ARGUMENT elements not hash-checked: `s.difference(d.values())` with unhashable values (TypeError)
**Status: REPAIRED (executor r3, driver run #3, 2026-10-29), Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
Witnesses `witnesses-r456/` (14): `c20_e007.py`, `c22_v000.py`, `c22_v001.py`, `c22_v002.py`, `c22_v003.py`, `c22_v004.py`, `c22_v006.py`, `c22_v007.py`, `c22_v010_tuple_values.py`, `c22_v011_dict_of_dicts.py`, `c22_v012_set_values.py`, `c22_v013_list_param.py`, `c22_v014_items.py`, `c22_v015_realistic.py`.

Driver repro: 16/16 family exemplars rc=0 Verification SUCCESS on main 8fe7204c3 at 2026-10-29T02:35Z, each violating under CPython (scratchpad/rt36/driver-repro.txt).

```
FAMILY F13 -- set-method ARGUMENT elements not hash-checked: `s.difference(d.values())` with unhashable values (TypeError)   (14)
  EXEMPLAR c22/v015_realistic.py  PROVED (rc=0 Verification SUCCESS):
    | #@ no_exception \all
    | def f(tags: Set[str], groups: Dict[str, List[str]]) -> int:
    |     rest = tags.difference(groups.values())
    |     return len(rest)
    CPython 3.14: f({'a'}, {'g': ['a']})  ->  VIOLATION TypeError cannot use 'list' as a set element (unhashable type: 'list')
  MECHANISM: #441's (set, difference / intersection / union / issubset / issuperset) rows accept any iterable argument; the
  element-level check exists only for sum / bytes / dict / startswith (route #441 residual 6), but CPython hashes
  the argument's ELEMENTS. `s.difference(d.values())` lowers to the receiver-erased opaque
  `(s_difference_1 (d_values_0 ()))` (mlw/e007). A `List[List[int]]` PARAMETER argument does not type-check
  (c20 e002 / e003), so the probes use dict views / locals.
  REPAIR: OBLIGATION: the argument of every set method that hashes its argument's elements (difference, intersection,
  union, issubset, issuperset, symmetric_difference, isdisjoint, update, *_update) gets #349 / #438's element
  hashability check, exactly as `set(xs)` does -- refuse when the element class is not derived hashable.
  MEMBERS: c20/e007.py c22/v000.py c22/v001.py c22/v002.py c22/v003.py c22/v004.py c22/v006.py c22/v007.py c22/v010_tuple_values.py c22/v011_dict_of_dicts.py c22/v012_set_values.py c22/v013_list_param.py c22/v014_items.py c22/v015_realistic.py
```

## REPAIR (executor r3, driver run #3, 2026-10-29, off db6c57253; annotations §7.204, translational §T.6.214)

Code inline in the #349 / #394 hashing pass of `_run_pipeline` (mirror twin `\trusted`; no emission change, no
new message). On a receiver derived `set` / `frozenset` (`_ty383`), each positional argument of `union` / `intersection` /
`difference` / `symmetric_difference` / `issubset` / `issuperset` / `isdisjoint` / `update` / `*_update` is a hashed
position exactly as `set(x)`'s argument: display elements, a comprehension's element, or the derived elements of any
other iterable (`_xe394` / `_ei383`), judged by the existing rules (`PYCSL-R349-UNHASHABLE-RECORD`; underivable under a
TypeError claim `PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM`). AUDIT of other hashing positions: `set()` / `frozenset()` /
`Counter()` / `dict()` / `fromkeys()` / `add` / `discard` / `remove` / `in` / subscripts were already positions.
Witnesses 7029-7034 (6 of the 14 probes; all 14 PROVED at base and are REFUSED). Control 7035
(`tags.difference(groups.values())` over `Dict[str, str]`): PROVED at base and candidate.

GATES (one candidate, one battery for #447 / #451 / #452 / #454 / #456 / #459; see the README run-#3 r3 entry): fidelity sync / mirror-check rc=0; root corpus 2569 base -> 2581 candidate .mlw, 0 MOVED, 3 GONE (5066 / 5071 / 5072, expected FAIL route-#375 witnesses `[*self]` / `(*self,)` / `g(*self)` on a field-less class: VERIFY-FAIL -> REFUSED by #454), 0 APPEARED; pyref 2186 / 2186 0 / 0 / 0; mirror 53 / 53 0 / 0 / 0 (no OWED proof); planes / ledgers: see the README entry.

## RESIDUALS: `dict.update(x)` (hashes x's keys) is not a new position; a set receiver whose class is underivable is not
judged.
