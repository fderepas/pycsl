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

## REPAIR (2026-10-26, e2 executor off 3b2d2e763; code + corpus + docs ffec1ac18 and follow-ups on this branch; inline in `_run_pipeline`, mirror twin `\trusted`, no new def, no emission change, ledger unchanged)
**Design: a TypedDict value is a `dict`; a key is READ only when positively REQUIRED.** (3) the functional form `X =
TypedDict("X", ..)` (any `typing` / `typing_extensions` spelling) is a typing construct for TC (t05 `TD(a=1).a` now
`PYCSL-TC-TYPING-CONSTRUCT-VALUE`). (1)+(2) On the resolved IR of each non-trusted function, `PYCSL-R398-TYPEDDICT-ACCESS` refuses:
in the body, `X.k` for a key of a file TypedDict unless `X` is `self` / `cls` or a variable of a known non-TypedDict type (t08); and
anywhere (contracts included) `X["k"]`, `X.get("k" ..)`, `X.pop`, `X.setdefault`, `"k" in X` for an OPTIONAL key -- `NotRequired`,
`Annotated`, `total=False` (inherited totality per class), non-literal totality / key set, a non-TypedDict base -- unless `X` is a
variable of a known type without that optional key (t06, t07, u48). No guard is admitted (the record has no presence bit; at base
the guarded `in` / `try` forms were ill-typed and `.get` of an optional key FAILED, so nothing measured is lost). Not taken: making
the field an `option` (an emission change). Witnesses 5639-5643 PROVED at 3b2d2e763 -> REFUSED; control 5682 (required key in a
contract and a body) PROVED both. Docs annotations §7.54, translational §T.6.65. Over-refusal: an optional key read after the
function stored it; `.k` on a receiver of unknown type in a file defining a TypedDict with a key `k`.
Over-refusal measured (emission sweeps vs a worktree at 3b2d2e763, logs `getting-better/repair-r393-400/gates/`): root corpus 2424 -> 2431 .mlw (7 new controls), 0 MOVED / 0 GONE / 0 APPEARED; python-reference 2186 -> 2186, 0 / 0 / 0; mirror 53 / 53, 0 / 0 / 0 (no OWED proof). The FIRST cut over-refused 3 files, each removed by a justified refinement: mirror `frontend/pure_ast` (`class PyCSLSyntaxError(SyntaxError)` raised `(msg, (file, line, col, text))`: the SyntaxError family is now MODELLED by its constructor shape instead of refused) and corpus 0889 / 0890 (a CONTRACT's `r.n` on a TypedDict is the spec notation for a required key, not a runtime attribute read).
