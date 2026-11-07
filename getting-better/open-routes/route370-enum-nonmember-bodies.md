# OPEN ROUTE #370 — ENUM CLASS-BODY NAMES THAT ARE NOT MEMBERS ARE READ AS MEMBERS (mangled private, nested class, descriptors, mutated `_ignore_`)
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r369 executor off dc378283 — sound refusal, see REPAIR). Was OPEN, Severity 1.** Red-team round 28 (2026-10-25, probes around the #357-#367 repairs); driver-reproduced on main 863a844aa (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt28/driver-repro.txt`).
Witnesses `witnesses-r370/`: `n02_explicit_mangled_private.py`, `n07_nested_class_not_member.py`, `n13_staticmethod_value.py`, `n14_partial_value.py`, `n15_classmethod_ref.py`, `n21_property_member.py`, `n22_ignore_append_later.py`, `n34_ignore_append_attr.py`, `n40_partial_by_value.py`, `n42_ignore_comma_member_attr.py`, `n43_mangled_intenum_cmp.py`, `n44_nested_class_member_cmp.py`, `n45_nested_def_member.py`, `n46_property_named_value.py`, `n55_intenum_nested_class_value.py`.

Enum tests the MANGLED `_C__x` form; the #367 repair checks only the source `__x` prefix (explicit `_C__B`: n02/n42/n43). `C.B.value` / `.name` lowers to `get_value(get_B ..)` for any class-body name: nested class, staticmethod, classmethod, partial, DynamicClassAttribute, def, property. `_ignore_` is read as its literal only (`_ignore_.append`, n22/n34). Slips past #367/#355/#356. CPython ValueError / AttributeError.

Repair: Member set by Enum's own rules: mangled-private test, drop nested classes / descriptors / functions / partials, refuse a non-literal or mutated `_ignore_`, refuse `.value` / `.name` on a non-member.

## REPAIR (2026-10-25, r369 executor off dc378283; code 88877615 / 6b575c0e / 38161b2e / 5a70413a / c2f46d20 / 710d3223, docs 2623c62a (annotations §7.35 / translational §T.6.46), corpus c2f46d20 + 710d3223, census 001405cc + 710d3223, route docs)
**Design (shared by #369-#372): sound refusals, no emission change, no new def** (inline in the #346-#349 / #360-#363 block and the
#339/#352 enum block of `_run_pipeline`, mirror twin `\trusted`), ledger 3. Two new refusal codes, `PYCSL-R369-DATACLASS-SPECIFIER` and
`PYCSL-R369-CONSTRUCTOR-ARITY`; #370 reuses `PYCSL-SEM-ENUM-MEMBER-OPERATION`, #371 / #372 reuse `PYCSL-R349-UNHASHABLE-RECORD`
(annotations §7.35, translational §T.6.46).
RULES (in the #339/#352/#367 enum block). (1) The private test runs on the MANGLED namespace key as `enum._is_private(cls, key)`
does (`_C__B` written explicitly is private; a source `__x` stays private). (2) A value is a MEMBER value only when it provably has
no `__get__` / `__set__` / `__delete__` and is no nested class: a literal, a display, an operator / f-string over those, an alias of
an earlier member, `auto()` / `member(..)` of `enum`; anything else (`staticmethod(len)` / `classmethod(len)` — already descriptors
—, `functools.partial(int)` — a method descriptor since 3.14 —, `types.DynamicClassAttribute(..)`, a module constant, any call)
has UNKNOWN status: neither a member nor an admitted class attribute, and the literal value list becomes unknown (`C(v)` refused).
(3) Route #356's class-object rule now admits `C.X` only for a member, or as the callee of a call to an own `def` /
`staticmethod(..)` / `classmethod(..)` binding: a nested class, `def`, property, descriptor or private name read as `C.B` (and
then `.value` / `.name`) is refused. (4) A `Load` of `_ignore_` in the class scope (`_ignore_.append("B")`) makes the member set
unknown: refused like a non-literal `_ignore_`. All `PYCSL-SEM-ENUM-MEMBER-OPERATION`.
**Probe table** (full pycsl proof via heavy.sh; base = dc378283 worktree):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| n02 explicit `_C__B = 2`, `C(2)` | 5010 | ValueError | rc=0 PROVED | rc=1 REFUSED PYCSL-SEM-ENUM-MEMBER-OPERATION |
| n07 nested class, `C.B.value` | 5011 | AttributeError | rc=0 PROVED | rc=1 REFUSED PYCSL-SEM-ENUM-MEMBER-OPERATION |
| n13 `staticmethod(len)`, `C.B.value` | 5012 | AttributeError | rc=0 PROVED | rc=1 REFUSED PYCSL-SEM-ENUM-MEMBER-OPERATION |
| n14 `functools.partial(int)`, `C.B.value` | 5013 | AttributeError | rc=0 PROVED | rc=1 REFUSED PYCSL-SEM-ENUM-MEMBER-OPERATION |
| n15 `classmethod(len)`, `C.B.value` | 5014 | AttributeError | rc=0 PROVED | rc=1 REFUSED PYCSL-SEM-ENUM-MEMBER-OPERATION |
| n21 `DynamicClassAttribute`, `C.B` | 5015 | AttributeError | rc=0 PROVED | rc=1 REFUSED PYCSL-SEM-ENUM-MEMBER-OPERATION |
| n22 `_ignore_.append`, `C(2)` | 5016 | ValueError | rc=0 PROVED | rc=1 REFUSED PYCSL-SEM-ENUM-MEMBER-OPERATION |
| n34 `_ignore_.append`, `C.B` | 5017 | AttributeError | rc=0 PROVED | rc=1 REFUSED PYCSL-SEM-ENUM-MEMBER-OPERATION |
| n40 partial, `C.B.name` | 5018 | AttributeError | rc=0 PROVED | rc=1 REFUSED PYCSL-SEM-ENUM-MEMBER-OPERATION |
| n42 `C._C__B.value` | 5019 | AttributeError | rc=0 PROVED | rc=1 REFUSED PYCSL-SEM-ENUM-MEMBER-OPERATION |
| n43 IntEnum `_C__B`, `C(2)` | 5020 | ValueError | rc=0 PROVED | rc=1 REFUSED PYCSL-SEM-ENUM-MEMBER-OPERATION |
| n44 nested class, `C.B.name` | 5021 | AttributeError | rc=0 PROVED | rc=1 REFUSED PYCSL-SEM-ENUM-MEMBER-OPERATION |
| n45 `def B`, `C.B.value` | 5022 | AttributeError | rc=0 PROVED | rc=1 REFUSED PYCSL-SEM-ENUM-MEMBER-OPERATION |
| n46 `property(..)`, `C.B.value` | 5023 | AttributeError | rc=0 PROVED | rc=1 REFUSED PYCSL-SEM-ENUM-MEMBER-OPERATION |
| n55 IntEnum nested class, `C.B.value` | 5024 | AttributeError | rc=0 PROVED | rc=1 REFUSED PYCSL-SEM-ENUM-MEMBER-OPERATION |
| control: `_ignore_` literal, member alias, a `def`; `C(2)`, `C.C2`, `C.A.value` | 5042 | ok | rc=0 PROVED | rc=0 PROVED |
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
**Residuals.** (1) Over-refusal: a member whose value is a module constant / a call that is not a descriptor (`A = K`, `A =
f()`) is now of unknown status — `C.A` and `C(v)` are refused (0 enum users in the corpora / pycsl_lib; the mirror's `_Precedence`
uses `_enum.auto()` and a member alias, unaffected). (2) Tuple-target bindings in the body (`A, B = 1, 2`) are not members (#367
residual). (3) The functional API (`Enum("C", "A B")`) is not classified. (4) `C.helper()` of an own def is admitted as before; its
lowering is unchanged.
