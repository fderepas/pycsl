# OPEN ROUTE #382 — CONTAINER VALUES AS SET-DISPLAY ELEMENTS ARE NEVER CHECKED
**Status: REPAIRED, candidate (gen #37, 2026-10-26; r381s executor off 7bf752d4e — sound refusal, see REPAIR). Was OPEN, Severity 1.** Red-team round 29 (2026-10-25, probes around the #226 increment and #369-#372); driver-reproduced on main 919533395 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt29/driver-repro.txt`).
Witnesses `witnesses-r382/`: `h34_deque_param.py`, `h35_typing_deque_param.py`, `h36_set_param.py`, `h37_simplens_param.py`, `h39_userlist_param.py`, `h40_ordereddict_param.py`, `h41_defaultdict_param.py`, `h42_array_param.py`, `h43_counter_param.py`, `h44_mutableset_param.py`, `h45_list_builtin_param.py`, `h46_dict_builtin_param.py`, `h54_typing_list_param.py`, `h55_typing_dict_param.py`, `h60_list_local_display.py`, `h61_list_of_list_elem.py`, `h62_list_loop_elem.py`.

`{xs}` with `xs` annotated list / List / dict / Dict / Set / MutableSet / deque / Deque / SimpleNamespace / UserList / OrderedDict / defaultdict / array / Counter, a list local display, `{xs[0]}` over `List[List[int]]`, `for y in xs: {y}`: proves under no_exception; CPython TypeError. (`hash(xs)`, `{xs: 1}`, `xs in {..}`, `s.add(xs)`, `frozenset(..)` are correctly refused.)

Repair: Apply the hash()/add/in container-type test in the set-display element position.

## gen #37 (2026-10-25) — r381 executor WIP (NOT landed, ungated)
Candidate WIP in `../pycsl-r381` (9cb374e71 #381 stdlib-base table + #383 aliases; 18acf06af #382 container test + #383 type
propagation; 5b063cdd0): `--no-proof` screen refuses all 47 #381-#383 witnesses (R349); no full proofs, sweeps or gates run;
over-refusal risk of the #383 `#UNK` rule unmeasured (mirror emit sweep required before landing). Measured live at base and NOT
yet witnessed: `s.add(d)` and `{d: 1}` with `d: deque` PROVE (contrary to this route's note); `types.MappingProxyType` is
classed hashable. Next: sweep 9cb374e71 alone first, then the full candidate.

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
