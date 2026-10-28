# OPEN ROUTE #383 — ELEMENT-CLASS SOURCES #372 DOES NOT DERIVE
**Status: REPAIRED, candidate (gen #37, 2026-10-26; r381s executor off 7bf752d4e — sound refusal, see REPAIR). Was OPEN, Severity 1.** Red-team round 29 (2026-10-25, probes around the #226 increment and #369-#372); driver-reproduced on main 919533395 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt29/driver-repro.txt`).
Witnesses `witnesses-r383/`: `h33_star_in_set.py`, `k14_type_alias.py`, `k15_dict_get.py`, `k17_dict_values_loop.py`, `k21_list_comp_subscript.py`, `k24_method_return.py`, `k25_any_param.py`, `k30_slice_elem.py`, `k38_items_loop.py`, `k39_alias_list_param.py`, `k40_alias_in_loop.py`, `k41_field_dict_get.py`, `k42_any_field.py`, `k43_method_return_self_field.py`, `k53_object_param.py`, `k54_typevar.py`.

Type aliases (`DD = D`, `DL = List[D]`), `m.get(..)`, loops over `.values()` / `.items()`, list comprehension then subscript, slice then subscript, method returns, `{*ds}`, and Any / object / TypeVar values or an Any field while the file has an unhashable class: `{..}` under no_exception proves; CPython TypeError.

Repair: Resolve module type aliases; element classes from `-> T` of methods and get/values/items, through comprehensions and slices; when underivable and the file has an unhashable class, refuse.

## REPAIR (2026-10-26, r381s executor off 7bf752d4e; code 324907ddc (from r381 WIP 9cb374e71) + 9942dc760 (from 18acf06af / 5b063cdd0, narrowed), corpus + census b89ed1f91, docs ed1448bd4 (annotations §7.46 / translational §T.6.57), route docs)
**Design (shared by #381-#383): sound refusals, no emission change, no new def, no new refusal code** (inline in the #346-#349 /
#364-#366 / #369-#372 block of `_run_pipeline`, mirror twin `\trusted`; reuses `PYCSL-R349-UNHASHABLE-RECORD`, message extended with
"or, when it cannot be derived, may have (routes #381-#383)"). Ledger 3, no axiom.
RULE. (#381) every base / annotation name outside the file is resolved through the file's imports and builtins to a qualified
name; a name in an allow-listed stdlib module (spec under the interpreter's stdlib dir) is imported and classified on the real
class: a base whose `__hash__` is None, whose hash delegates to its contents (`slice` / `memoryview` / `types.MappingProxyType` /
`weakref.ref` or a subclass), or that is unknown (non-stdlib / relative / star import, a name bound otherwise) decides UNHASHABLE in
#371's MRO walk; a hashable one is skipped. (#382) the container mark is applied at every depth of every hashing position (set
element, dict key, `add` / `in` / subscript / `hash`), and each outside class name in a hashed value's classes is read by its real
class (container / `__hash__ = None` -> unhashable; a value DECLARED `Any` / `object` / TypeVar / unknown import / bare `tuple` ->
`#UNK`, any unhashable class of the file). (#383) a per-function type propagation (module type aliases, `get` / `pop` / views /
loops / comprehensions / slices / `*x` / method and function `-> T` / constructors / common builtins), least fixpoint over locals;
an UNDERIVABLE form is `#UND` (no class), and an `Any` reached through a container (`Dict[str, Any]`'s `.get`) is underivable.
**Over-refusal measured and narrowed.** The WIP as cherry-picked (#UNK for every underivable form) refused 13 of 53 mirrors and 5
PROVED corpus files (0893, 0951, 0956-0959): an alias unresolved in #366's field rule, a field absent from one member of a
union-typed receiver, `i = i + 1` poisoned before its first binding was typed, `Dict[str, Any]` values, a bare `Tuple`
annotation (pycsl.py `_merge_records_best_of_n`). Each narrowed soundly (alias followed; an absent field counts through the file
subclasses defining it unless the attribute may be bound otherwise — witness 5384; least fixpoint; underivable = no class, as at
base). Step 1 (324907ddc alone) was measured separately: root 2411/2411, pyref 2186/2186, mirror 53/53, all 0/0/0; lib identical.
**Probe table** (full pycsl proof via heavy.sh; base = 7bf752d4e worktree `pycsl-r381s-base`; CPython checked for every file):
| witnesses | corpus | CPython | base | after |
|---|---|---|---|---|
| #381 h01-h13, h48, h49, h51, h52 (14) | 5330-5343 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R349-UNHASHABLE-RECORD |
| #382 h34-h46, h54, h55, h60-h62 (17) | 5344-5360 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| #383 h33, k14-k54 (16) | 5361-5376 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| NEW `s.add(d)` / `{d: 1}`, `d: deque` (route #382 status note) | 5377 / 5378 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| NEW `types.MappingProxyType` (two spellings), `memoryview` (ValueError), `slice`, `weakref.ref` | 5379-5383 | TypeError / ValueError | rc=0 PROVED | rc=1 REFUSED |
| NEW field defined only by a file subclass (`e: B`, `{e.d}`) | 5384 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| NEW `from collections import *; class D(UserList)` (driver probe a1_star) | 5385 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| controls: hashable outside bases; hashable values / components; #383 sources over a FROZEN class; hashable stdlib values | 5390-5393 | ok | rc=0 PROVED | rc=0 PROVED |
Census rows for 5330-5385 (and 3601) produced by `_census_row` (57 REFUSAL).
**Sweeps (final code 9942dc760).** Root 2411 base / 2414 candidate .mlw: 0 MOVED / 1 GONE / 0 APPEARED (4 new control sources); the
GONE is 3601 (`# pycsl-expected: FAIL`, VERIFY-FAIL at base, now REFUSED: `func in g['G']['methods']` with `func: Dict` and an
`Any` container — sound, a set container raises TypeError; its census row records REFUSAL), compare rc=0 with `--expect-gone
3601_gen37_r2c_hval_mem_opaque_false_claim`. Pyref 2186 / 2186 0/0/0. Mirror-emit-sweep 53 / 53 0/0/0 — no OWED proof.
`pycsl_lib` emission screen 104 files identical to base (87 rc=0 / 17 rc=1). So 0 PASS-expected file newly refused in any plane.
**Gates** (logs in the executor scratchpad `r381s/gates/`; rc): check-self-annotate-sync.sh && self-annotate-mirror-check.sh rc=0
(926 verbatim, 53 mirrors in sync); byte-diff-compare root rc=0 (with the one declared `--expect-gone` 3601; rc=1 without it),
pyref rc=0, mirror rc=0; run-soundness-planes.sh fast **61/61** rc=0 (`--slow` NOT run); doc-coherency --check rc=0;
check-refusal-witness-coverage rc=0 (310 demonstrated / 5 undemonstrated = ceiling 5); check-refusal-advice-audited rc=0 (145 / 204,
floor 133); `\trusted` count 448 (unchanged); no emission change, so no new axiom (ledger unchanged).
**Residuals (the rule is still a DENY-list).** (1) An underivable value (unknown callee / receiver, un-annotated return, `Any`
through a container) is not checked. (2) A value declared `Any` / `object` / TypeVar / bare `tuple`, or of a class imported from a
non-stdlib module, is checked only against the FILE's unhashable classes: a builtin container reaching it (`d: Any` given a list)
or a cross-module unhashable class (driver probes a4_xmod `from s1lib import D`, a11_xmod_alias `D = E`: PROVED at base and after)
is not seen. (3) Outside bases from local (non-stdlib) modules count as unhashable (sound, possibly over-refusing; 0 measured
users). (4) The classification imports stdlib modules of the RUNNING interpreter (3.14), so a stdlib class's hashability is that
interpreter's (`slice` / `memoryview` are classed unhashable regardless, as their hash depends on contents).

## REPAIR ADDENDUM — ALLOW-LIST POLARITY (2026-10-26, rh1 executor off b62ff2e23; code 948b0ba72, corpus + census 6d4cac6a3, docs annotations §7.47 / translational §T.6.58)
**Rule.** A hashed value whose class set holds `#UNK` (declared `Any` / `object` / a TypeVar, a class of a non-stdlib module, a
`Dict[str, Any]` subscript value) is refused in every hashing position unless its class is known hashable: `#UNK` now adds the
container mark `#UB` as well as the file's unhashable classes (r381s "Variant A"). Same code / message
(`PYCSL-R349-UNHASHABLE-RECORD`), inline in the #349 block of `_run_pipeline` (mirror twin `\trusted`), no emission change,
no new def, ledger unchanged.
**Over-refusal, measured (byte-diff vs a b62ff2e23 worktree).** Variant A as ported: root 2421/2421 0 MOVED / 0 GONE / 0 APPEARED
(the sweep shows `1723_route212_verify_imports_control` GONE in BOTH candidate sweeps — its `--verify-imports` dependency proof
times out under load; re-emitted standalone, byte-identical), pyref 2186/2186 0/0/0, `pycsl_lib` 104/104 identical (87 rc=0),
mirror **2/53 GONE**: (a) `module6_whyml/functions.py` `_compute_return_type` l.536 `self._record_types[func['return_value_type']]`
(`func: Dict[str, PyVal]`, `PyVal = Any`); (b) `pycsl.py` `_merge_records_best_of_n` l.802-810 (`occ.get(k, 0)`, `best[key]`,
`key not in best`), all from `k = _record_key(rec)` declared `-> "Tuple"` and `order: "List[Tuple]"`.
**Narrowing (both sites analysed).** (a) is PRECISE: it sits in the first statement of the body of
`elif func.get("return_value_type") in self._record_types:` — the same value was just hashed by that test. Rule: in the first
call-free statement of an `if A in B:` body, `B[A2]` with `A2` the value of `A` (`x.get(K)` == `x[K]` for a `Dict`-annotated
local, constant `K`) keeps the deny-list check only. (b) is GENUINELY UNKNOWN-TYPED: `_record_key` builds its tuple from
`rec: dict` why3-JSON fields (`loc.get("file-name")` ...), whose values are `Any` in every derivation; no precise type exists.
Refusing it GONEs a proved mirror, so an UN-PARAMETERISED `tuple` / `Tuple` now marks `#UNKT` and keeps the deny-list check
only (a residual, not a site exemption: `t: tuple` holding a list still PROVES — probe r3 / p03).
After narrowing: root 2421/2421 0/0/0 (same 1723 load flake, re-emitted identical), pyref 2186/2186 0/0/0, mirror 53/53 0/0/0
(no OWED proof), `pycsl_lib` identical. Unnarrowed candidate kept as a patch (scratchpad `rh1/candidate-AG.patch` = Variant A +
the guarded re-hash: mirror 1/53 GONE, pycsl.py).
**Probe table** (full proof via heavy.sh; REFUSED rows by the --no-proof screen, the refusal precedes proving; CPython checked for every file):
| probe | corpus | CPython | base b62ff2e23 | candidate |
|---|---|---|---|---|
| `d: Any`, `{d}` (residual probe r1) | 5500 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| `m: Dict[str, Any]`, `{m["a"]}` (residual probe r4) | 5501 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| `d: object`, `{d: 1}` | 5502 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| `d: Any`, `s.add(d)` | 5503 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| `from multi_file_lib.r383a_eqlib import D` (plain `__eq__`, no stdlib base), `{d}` | 5504 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| same, `import D as E; D = E` | 5505 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| `d: T` (TypeVar), `{d}` | 5506 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| controls: int / str / `Tuple[str, str]` / `Optional[str]` values; frozen file dataclass | 5510 / 5511 | ok | rc=0 PROVED | rc=0 PROVED |
| driver probes a4_xmod / a11_xmod_alias (`D(UserList)` in a user module, `--import-path lib`) | (5449 / 5450) | TypeError | rc=1 REFUSED by S1 already | rc=1 REFUSED by S1 |
| `t: tuple` holding a list (residual probe r3) | — | TypeError | rc=0 PROVED | rc=0 PROVED (#UNKT residual) |
| `from mylib import K` (frozen dataclass), `{k}` | — | ok | rc=0 PROVED | rc=1 REFUSED (over-refusal; 0 corpus / mirror / lib users) |
**Residuals.** (1) UNDERIVABLE values (`#UND`: unknown callee / receiver, un-annotated return, `.get` of a `Dict[str, Any]`,
an `Any` element of a declared container) are still unchecked — the "Variant B" polarity (`#UND` refused too) is not measured
here. (2) Un-parameterised `tuple` / `Tuple` (above). (3) A hashable class of a non-stdlib module is refused (its module is not
inspected). (4) The guarded re-hash trusts that attribute reads are pure and that `B`'s `__contains__` and `__getitem__` agree
on hashing (true for dict / set; a user class whose `__contains__` does not hash but whose `__getitem__` does is only
deny-list checked there).
**Gates (candidate 6d4cac6a3 + docs).** fidelity `check-self-annotate-sync.sh && self-annotate-mirror-check.sh` rc=0 (926 un-trusted
mirror functions verbatim, 53 mirrors in sync); byte-diff root rc=0 (2421/2421 0/0/0 after re-emitting the 1723 flake) and pyref
rc=0 (2186/2186 0/0/0); mirror-emit-sweep 53/53 0/0/0 (no OWED proof); `pycsl_lib` screen identical; `run-soundness-planes.sh`
fast 61/61 rc=0; `check-refusal-witness-coverage.py` rc=0 (312 demonstrated); `check-refusal-advice-audited.py` rc=0 (message
unchanged); `doc-coherency.py --check` rc=0; `\trusted` lines 448 (unchanged); no axiom, ledger unchanged.

## #UND RESIDUAL: route R-gate CERTIFIED-BOUNDARY (2026-10-28, executor rg off 289fe6029, wall cycle #2 `dict-value-model-r3`)
The review `getting-better/dict-value-model-r3-response.md` §5 proposed R-gate: refuse a `#UND` / no-source hashed value only in a
function claiming `no_exception \all`, and leave it ambient elsewhere. It was **not built**. Spike S0
(`getting-better/dict-value-model-r3-impl.md` §R) refuted its premise that an ambient exception ends a function only abnormally:
- a `return` in `finally:` swallows the hash TypeError, and an un-claimed `ensures` is PROVED false on a normal return (open route
  #431, witnesses l3o / l3p);
- a claimed caller of an un-claimed `#UND`-hashing callee PROVES (open route #430, l3d).

Measured gated cost, for when the route is reopened:
- 0 claimed `#UND` sites in the 53 mirrors (ungated: 568 UND sites in 24 mirrors);
- 0 in `pycsl_lib` and 0 in pyref;
- 1 root PASS file, `6336_r427_ctl_snapshot_iteration.py` (`d[k + 100]`, `d[k + 300]`: an int key derived as `#UND`).

The residual stays as documented above. It reopens when #431 is repaired: re-run spike S0, then build R-gate per the impl doc §4.
