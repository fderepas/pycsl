# OPEN ROUTE #369 — DATACLASS FIELD SPECIFIERS ARE RECOGNISED BY LITERAL SPELLING ONLY (InitVar / KW_ONLY / ClassVar / field aliases)
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r369 executor off dc378283 — sound refusal, see REPAIR). Was OPEN, Severity 1.** Red-team round 28 (2026-10-25, probes around the #357-#367 repairs); driver-reproduced on main 863a844aa (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt28/driver-repro.txt`).
Witnesses `witnesses-r369/`: `d01_initvar_alias.py`, `d03_classvar_alias_ctor.py`, `d04_field_alias_init_false.py`, `d06_kwonly_alias.py`, `d07_initvar_alias_invariant.py`, `d11_classvar_alias_read_nodefault.py`, `d12_typing_module_alias_classvar.py`, `d14_initvar_alias_assign.py`, `d15_kwonly_alias_assign.py`, `d17_classvar_alias_invariant_ctor.py`, `d18_initvar_alias_arith.py`, `d22_field_alias_default_value.py`, `d26_classvar_alias_shifts_positional.py`, `d27_field_alias_init_false_ctor_arg.py`, `d28_kwonly_alias_positional.py`, `d29_field_alias_kw_only.py`, `d31_classvar_alias_read_value.py`, `d32_field_kw_only_required.py`.

Detection keys on the head name `InitVar` / `KW_ONLY` / `ClassVar` / `field`: an alias (`from dataclasses import InitVar as IV`, `typing as t; t.ClassVar`, `field as fld`) is an ordinary field, and `fld(default=7)` reads as default 0; a required `field(kw_only=True)` (d32) is mis-modelled too. Slips past #361/#362/#347/#146. CPython AttributeError / TypeError / wrong values (7, 5, 0, -1).

Repair: Resolve specifier names through the file's import/alias table, or refuse any dataclass annotation head / default call it cannot resolve; honour `field(kw_only=True)` without a default.

## REPAIR (2026-10-25, r369 executor off dc378283; code 88877615 / 6b575c0e / 38161b2e / 5a70413a / c2f46d20 / 710d3223, docs 2623c62a (annotations §7.35 / translational §T.6.46), corpus c2f46d20 + 710d3223, census 001405cc + 710d3223, route docs)
**Design (shared by #369-#372): sound refusals, no emission change, no new def** (inline in the #346-#349 / #360-#363 block and the
#339/#352 enum block of `_run_pipeline`, mirror twin `\trusted`), ledger 3. Two new refusal codes, `PYCSL-R369-DATACLASS-SPECIFIER` and
`PYCSL-R369-CONSTRUCTOR-ARITY`; #370 reuses `PYCSL-SEM-ENUM-MEMBER-OPERATION`, #371 / #372 reuse `PYCSL-R349-UNHASHABLE-RECORD`
(annotations §7.35, translational §T.6.46).
RULES. (a) Every `@dataclass` annotation head (string annotations parsed once, one subscript stripped) and default callee is
RESOLVED through the file's imports and module-level aliases (stdlib origin, file class / def, builtin, `unbound`, or UNKNOWN: a
non-stdlib / relative / star import, a name bound otherwise). `PYCSL-R369-DATACLASS-SPECIFIER`: a specifier spelled other than by
its own name (`IV`, `CV`, `KO`, `K`, `fld`), a specifier spelling resolving elsewhere, an UNKNOWN head or default callee, a default
call of a file `def` (it may return a `Field`), an annotated member nested in class-body control flow, and a `field(..)` with a
positional / `**` / unknown / repeated keyword, both defaults, or a non-literal `init` / `kw_only`. (A non-literal `dataclass`
decorator — `dataclass as dc`, a rebound name — was already refused at base by Module 3's decorator-binding rule, routes #130-#133,
measured; the check written for it was unreachable and was dropped so as not to add an undemonstrable raise site.) (b)
`PYCSL-R369-CONSTRUCTOR-ARITY`: a call `C(..)` of a file class whose constructor is known (first C3-MRO class with a plain
`def __init__`, else a dataclass's synthesized `__init__` in CPython's field order — positional, then keyword-only by `kw_only=True`
/ `field(kw_only=..)` / after `KW_ONLY`; InitVar in, ClassVar / `init=False` out —, else `object.__init__`) with too many
positionals, an unknown / repeated / positional-only keyword, or a missing required parameter, in any non-trusted function. This is
what makes d12 (`t.ClassVar` IS recognised; `D(1, 5)` simply was never arity-checked) and d32 (required `field(kw_only=True)`) fail,
and it closes NEW latent false proofs with LITERAL spellings (5008 explicit `__init__`, 5009 plain dataclass, 5037 literal
`KW_ONLY`, 5038 literal `field(init=False)`: all PROVED at base, CPython TypeError).
**Probe table** (full pycsl proof via heavy.sh on the filed corpus copies; base = dc378283 worktree):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| d01 `InitVar as IV`, `d.k` | 4990 | AttributeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-DATACLASS-SPECIFIER |
| d03 `ClassVar as CV`, `D(1, 5)` | 4991 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-DATACLASS-SPECIFIER |
| d04 `fld(init=False)` read | 4992 | AttributeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-DATACLASS-SPECIFIER |
| d06 `KW_ONLY as KO`, `d._` | 4993 | AttributeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-DATACLASS-SPECIFIER |
| d07 IV hides #362's invariant refusal | 4994 | -1 | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-DATACLASS-SPECIFIER |
| d11 `CV` without value read | 4995 | AttributeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-DATACLASS-SPECIFIER |
| d12 `t.ClassVar`, `D(1, 5)` | 4996 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-CONSTRUCTOR-ARITY |
| d14 `IV = InitVar` | 4997 | AttributeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-DATACLASS-SPECIFIER |
| d15 `K = KW_ONLY` | 4998 | AttributeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-DATACLASS-SPECIFIER |
| d17 CV, `D(1, 5)` under ensures | 4999 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-DATACLASS-SPECIFIER |
| d18 IV read as argument | 5000 | AttributeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-DATACLASS-SPECIFIER |
| d22 `fld(default=7)` | 5001 | 7 | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-DATACLASS-SPECIFIER |
| d26 CV shifts positionals | 5002 | 5 | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-DATACLASS-SPECIFIER |
| d27 `fld(init=False, default=4)` + arg | 5003 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-DATACLASS-SPECIFIER |
| d28 KO, positional kw-only | 5004 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-DATACLASS-SPECIFIER |
| d29 `fld(kw_only=True)` | 5005 | 0 | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-DATACLASS-SPECIFIER |
| d31 CV read as argument | 5006 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-DATACLASS-SPECIFIER |
| d32 required `field(kw_only=True)` missing | 5007 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-CONSTRUCTOR-ARITY |
| NEW latent: explicit `__init__(self, x)`, `D(1, 5)` | 5008 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-CONSTRUCTOR-ARITY |
| NEW latent: one-field dataclass, `D(1, 5)` | 5009 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-CONSTRUCTOR-ARITY |
| NEW latent: `x: int = mk()`, `mk` returns `field(default=7)` | 5036 | 7 | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-DATACLASS-SPECIFIER |
| NEW latent: literal `KW_ONLY`, `D(1, 2)` | 5037 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-CONSTRUCTOR-ARITY |
| NEW latent: literal `field(init=False, default=4)`, `D(1, 2)` | 5038 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-CONSTRUCTOR-ARITY |
| control: literal `t.ClassVar` / InitVar / KW_ONLY / `field(init=False)`, `D(1, 5, y=2).x == 1` | 5040 | 1 | rc=0 PROVED | rc=0 PROVED |
| control: well-formed explicit-`__init__` and kw-only dataclass calls | 5041 | 9 | rc=0 PROVED | rc=0 PROVED |
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
**Residuals.** (1) `*` / `**` arguments, `super().__init__(..)` / `C.__init__(self, ..)` / `cls(..)` calls, a `__new__` or
metaclass on the MRO, and imported classes are not arity-checked. (2) Over-refusal: a dataclass annotation head imported from a
non-stdlib module (it may re-export `ClassVar`) and a default call of a file function are refused (0 users in the census). (3)
`make_dataclass(..)`, `dataclasses.replace(..)` are not modelled (unchanged). (4) A dataclass default that is a mutable instance of
an unhashable class (CPython ValueError at class creation) is module-level, outside verified functions.
