# OPEN ROUTE #398 — TypedDict VALUES ARE MODELLED AS RECORDS WITH EVERY KEY PRESENT AND ATTRIBUTE ACCESS ALLOWED
**Status: OPEN, Severity 1.** Red-team round 31 (2026-10-26, probes around systematic rules S1/GD/TC/SB and the §7.46/§7.47 hash rules); driver-reproduced on 7859e8fb0 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt31/driver-repro.txt`).
Witnesses `witnesses-r398/`: `t05_typeddict_functional.py`, `t08_typeddict_field_attr.py`, `t06_typeddict_notrequired_key.py`, `t07_typeddict_total_false.py`, `u48_functional_notrequired.py`.

```
#398 TypedDict VALUES ARE MODELLED AS RECORDS WITH EVERY KEY PRESENT AND ATTRIBUTE ACCESS ALLOWED  [slips past TC §7.44]
  t08  d: TD (TC admits TD in an annotation); `d.a` no_exception PROVED                           CPython AttributeError
  t05  TD = TypedDict("TD", {"a": int}) (functional form: TC never sees a ClassDef); TD(a=1).a    AttributeError
  t06  `b: NotRequired[int]`; d["b"]                                                              KeyError
  t07  `class TD(TypedDict, total=False)`; d["a"]                                                 KeyError
  u48  functional TD with NotRequired key; d["b"]                                                 KeyError
  WhyML: `type td = { mutable a: int; mutable b: int }`, `d["b"]` -> `d.b`. (Refused correctly: TD(..) construction, u44/u47;
  del/pop/clear, u39-u41. Over-refusal noted: u45 `d: TD = {"a": 1}` with NotRequired b refused "missing required key".)
  REPAIR: (1) refuse `.attr` on a TypedDict-typed value (it is a dict); (2) a read `d[k]` of a key that is NotRequired /
  under total=False (incl. inherited totality) is a KeyError trigger under no_exception unless guarded by `k in d`; model
  the record field as option; (3) TC must recognise the functional forms `X = TypedDict("X", ..)` (and NamedTuple / Enum
  functional forms) as typing constructs.
```
