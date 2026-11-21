# OPEN ROUTE #372 — THE CLASS OF A HASHED ELEMENT IS NOT DERIVED FROM FIELDS OR SUBSCRIPTS
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r369 executor off dc378283 — sound refusal, see REPAIR). Was OPEN, Severity 1.** Red-team round 28 (2026-10-25, probes around the #357-#367 repairs); driver-reproduced on main 863a844aa (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt28/driver-repro.txt`).
Witnesses `witnesses-r372/`: `h18_list_index_not_hash.py`, `h52_record_field_elem_set.py`, `h55_tuple_index_elem_set.py`, `h70_self_field_elem_set.py`, `h73_dict_items_value.py`.

`{r.d}`, `{self.d}` (typed record fields), `{t[0]}`, `{m[0]}`, `{xs[0]}` (subscripts of fully annotated tuple / dict / list parameters) are never hash-checked; h18 is #349 residual (1). CPython TypeError unhashable.

Repair: Derive the element class from field annotations and Tuple / Dict / List subscripts; refuse when unknown.

## REPAIR (2026-10-25, r369 executor off dc378283; code 88877615 / 6b575c0e / 38161b2e / 5a70413a / c2f46d20 / 710d3223, docs 2623c62a (annotations §7.35 / translational §T.6.46), corpus c2f46d20 + 710d3223, census 001405cc + 710d3223, route docs)
**Design (shared by #369-#372): sound refusals, no emission change, no new def** (inline in the #346-#349 / #360-#363 block and the
#339/#352 enum block of `_run_pipeline`, mirror twin `\trusted`), ledger 3. Two new refusal codes, `PYCSL-R369-DATACLASS-SPECIFIER` and
`PYCSL-R369-CONSTRUCTOR-ARITY`; #370 reuses `PYCSL-SEM-ENUM-MEMBER-OPERATION`, #371 / #372 reuse `PYCSL-R349-UNHASHABLE-RECORD`
(annotations §7.35, translational §T.6.46).
RULE (in route #349's per-function hashing check). `_eh372[id(e)]` adds to the classes of a hashed expression: for `b.f`
with `b`'s class known (typed name, `self`, constructor call, or itself a field), the classes of `f` over the receiver's base
closure, from class-body and `self.f: T` annotations and from every `self.f = e` store in a method (a typed parameter's annotation,
a constructor call, a literal's type, an operator → int, a display → list / dict, anything else `#UNK`: with an unhashable class in
the file a `#UNK` element is refused); for `b[i]` with `b` a name / field annotated `List` / `Sequence` / `Deque` (element),
`Dict` / `Mapping` / ... (value), `Tuple` (the `i`-th component for a literal index, else all); and for a `for` / comprehension
target over such a name or field, the element / key / components (into the name's hashed classes). Three passes reach nested
forms (`r.e.d`).
**Probe table** (full pycsl proof via heavy.sh; base = dc378283 worktree):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| h18 `xs: List[D]`, `{xs[0]}` (#349 residual 1) | 5031 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R349-UNHASHABLE-RECORD |
| h52 `{r.d}`, `self.d = d` from `d: D` | 5032 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R349-UNHASHABLE-RECORD |
| h55 `t: Tuple[D, int]`, `{t[0]}` | 5033 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R349-UNHASHABLE-RECORD |
| h70 `{self.d}` in a method | 5034 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R349-UNHASHABLE-RECORD |
| h73 `m: Dict[int, D]`, `{m[0]}` | 5035 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R349-UNHASHABLE-RECORD |
| NEW shape: `for d in ds` (`ds: List[D]`), `{d}` | 5039 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R349-UNHASHABLE-RECORD |
| NEW shape: `{r.e.d}` (field of a field) | 5045 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R349-UNHASHABLE-RECORD |
| control: `{r.f}` frozen field, `{t[1]}` int component, `{m[0]}` frozen value | 5044 | ok | rc=0 PROVED | rc=0 PROVED |
Controls 5040-5044 PROVED at base and after (regression controls; no over-refusal existed at base). The census run (`_census_row`,
full pipeline) of every FAIL witness 4990-5039 / 5045 at the final candidate records REFUSAL for all 51.
**Census / blast radius** (shared): before landing, 497 `@dataclass` classes / 1000 annotated members / 103 `field(..)` calls over
both corpora, the 53 mirrors and `pycsl_lib` were resolved by a prototype of rule (a): 0 aliases, 0 unknown heads once a
module-level string alias (`Expr = "Leaf | Bad"`), an int stub alias (`Term = 0`) and an unbound forward name are read as
non-specifiers. The first candidate sweep showed 15 root GONE (0950-0965 string-alias heads, 4942 `p: "P"`): a string annotation
parsed twice gave a fresh node whose resolution was looked up under the wrong id, plus a variable-name clash in the arity block
(`'bool' object has no attribute 'get'`); fixed in 5a70413a, re-emitted byte-identical, re-swept to 0/0/0. Final sweeps (code
710d3223): root 2341 base / 2346 candidate .mlw, 0 MOVED / 0 GONE / 0 APPEARED (5 new control sources); pyref 2186 / 2186 0/0/0
(`--min-files 2000`); mirror-emit-sweep 53 / 53 0/0/0 (`--min-files 50`) — **no OWED proof**. So 0 non-witness users of any newly
refused shape in any plane, including the arity check over explicit `__init__`s.
**Gates** (logs in the executor scratchpad; rc): witnesses / controls above (full proof via heavy.sh, base dc378283 worktree vs
candidate); byte-diff-compare root rc=0, pyref rc=0, mirror rc=0 (above); check-self-annotate-sync.sh rc=0 (926 verbatim);
self-annotate-mirror-check.sh rc=0 (53); run-soundness-planes.sh fast **61/61** rc=0 (`--slow` NOT run); check-getattr-erasure rc=0
(DECLARED 0); check-stdlib-modules-verify rc=0 (one command via heavy.sh: 104 modules, 83 VERIFY, the known 21 non-verifying); doc-coherency --check rc=0; check-assumed-facts rc=0 (85 facts, all reviewed families; ledger 3);
check-dropped-mutation rc=0 (0 / 51 / 5 / 0); check-refusal-witness-coverage rc=0 (303 demonstrated / 5 undemonstrated = ceiling
5; rows 4990-5039 + 5045 via `_census_row`); check-trusted-reasons rc=0 (420 / 420, ratchet 259); check-trusted-raises-honesty rc=0
(19 / 61, ratchet 61); check-assigns-underdeclaration --transitive rc=0 (TRAP 3, HOLE 0); check-mirror-coverage rc=0 (549 / 41).
**Residuals.** (1) An element whose class comes from a callee's return, a subscript of a subscript, an un-annotated
container's display elements (`xs = [d]; {xs[0]}`) or a field stored only from an un-annotated value of a class without
unhashable classes in the file is not checked. (2) Over-refusal: a field stored from an unknown value (`#UNK`) hashed in a file that
has any unhashable class (0 users measured).
