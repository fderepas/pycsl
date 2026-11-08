# OPEN ROUTE #442 — #432 NARROWING TRUSTS isinstance(R, E) FOR ANY E THAT IS NOT LITERALLY object / Any
**Status: REPAIRED (executor h442, driver run #3, 2026-10-28), Severity 1.** Red-team round 35 (2026-10-28, SYSTEMATIC BUILTIN-PRECONDITION CENSUS after #432-#439 on daaf6ea78: 860 probes / 452 fully proved / 175 confirmed (156 new + 19 inside #432's documented residual); rt34's 63 all closed). Census TSV `scratchpad/rt35/census.tsv`; findings `scratchpad/rt35/FINDINGS.txt` (the family text below is quoted from it).
Witnesses `witnesses-r442/` (6): `w007_isinstance_alias_type.py`, `c000_isinst_alias_O.py`, `c001_isinst_tuple_alias.py`, `c007_isinst_hashable.py`, `c008_isinst_typing_hashable.py`, `c021_isinst_cls_var.py`.

Driver repro: 7/7 family exemplars (A1 n002, A2 s106, B1 k001 + e017, B2 a001, C c007, D b000) rc=0 Verification SUCCESS on main f1c249c4e at 2026-10-28T19:25Z, each violating under CPython (scratchpad/rt35/driver-repro.txt).

```
#442 #432 NARROWING TRUSTS isinstance(R, E) FOR ANY E THAT IS NOT LITERALLY object / Any   (6)
  c007  `if isinstance(x, Hashable): x.upper()` x: Optional[str] PROVED; f(None)        CPython AttributeError.
  w007 / c000 `T = object` / `O = object` aliases; c001 `T = (str, object)`; c021 class attribute `H.t = object`;
  c008 typing.Hashable.
  REPAIR (proposed, allow-list / refuse by default): isinstance narrows only by a class expression RESOLVED to concrete classes none of which is a superclass of NoneType;
  an unresolved name / alias / attribute / tuple variable does not narrow.
```

## REPAIR (executor h442, driver run #3, 2026-10-28, off fa7cbb1aa; annotations §7.150, translational §T.6.160)

Code inline in `_run_pipeline` (src/pycsl/pycsl.py), in route #432's narrowing leaves (no new def in a mirrored file,
no axiom, no emission change). ALLOW-LIST: the leaf `isinstance(R, E)` narrows only when `isinstance` is never bound in
the file (no def / store / import / class of that name, no star import -- before, only function-local bindings were
checked) and every element of `E` (a `Name`, or a literal tuple of `Name`s) is RESOLVED: a name never bound in the file
(no store, def, argument, class, import, star import) naming a real builtin class `C` with `type(C) is type` and
`not issubclass(type(None), C)` (decided on the real class: `object` fails). Everything else -- an attribute
(`typing.Hashable`, `H.t`, `builtins.str`), an alias (`T = object`), an imported name (`Hashable`), a tuple variable,
a PEP 604 union, a FILE class -- contributes nothing (the receiver keeps its derived classes, so `Optional[str]` keeps
`None` and #432 refuses). A file class does not narrow: an `Optional` / `Union` of file classes does not type-check
after narrowing at base (measured: `Optional[P]` / `Union[P, Q]` with `isinstance(x, P)`, Why3 type error), and no
corpus PASS file narrows by one, so the branch was dropped rather than shipped untested.

Witnesses 6750-6755 (the 6 red-team probes): PROVED at base fa7cbb1aa, REFUSED at the candidate
(PYCSL-R432-OPTIONAL-RECEIVER-ATTRIBUTE: the guard no longer narrows). Controls 6780 (`isinstance(x, str)`), 6781
(`(str, bytes)`), 6782 (`isinstance(x, int)` before `x.bit_length()`): PROVED at base and candidate; g4's 6515-6518 /
6522 still PROVED.

GATES: see route443-any-element-method-receiver.md's REPAIR (one candidate, one gate battery).

## RESIDUALS (honest)

Over-refusal by design (cost 0 in the corpus): narrowing by a file class, by `builtins.str` (an attribute), by an
imported concrete class (`from decimal import Decimal`), by `str | bytes`. A builtin name is trusted to mean the real
builtin when the FILE never binds it; a binding through `builtins.str = ...` / `globals()` mutation or another module
patching `builtins` is not seen.
