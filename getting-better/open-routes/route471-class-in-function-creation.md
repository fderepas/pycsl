# OPEN ROUTE #471 — CLASS STATEMENT EXECUTED INSIDE A FUNCTION BODY: route #461 creates (with CPython's machinery) only the classes of the module top level and of the class bodies it reaches; a `class` statement inside a claimed def, a nested def, an un-claimed callee, a method or an `if` arm is lowered as a record type with no creation check, so a local class CPython REJECTS (bool base, int+str layout, two __slots__ bases, duplicate base, MRO conflict, dataclass mutable default / frozen-from-non-frozen / order+__lt__ / field() without annotation, NamedTuple order / _x, Enum duplicate / extension / IntEnum non-int, unknown class keyword, metaclass=5, __init_subclass__ raising, total_ordering without ordering) proves (TypeError / ValueError when f runs)
**Status: REPAIRED (executor x2, driver run #3, 2026-10-29), Severity 1.** Red-team round 38 (2026-10-29, on a9eac4a08 after #460-#462: 688 probes / 155 proved / 142 confirmed; rt37's 83 all closed except #463 / #464). Census TSV `scratchpad/rt38/census.tsv`; the family block below is quoted from `scratchpad/rt38/FINDINGS.txt`.
Witnesses `witnesses-r471/` (18): `g13_k130_int_str_layout.py`, `g13_k131_namedtuple_underscore.py`, `g13_k134_enum_extend.py`, `g13_k135_unknown_class_kw.py`, `g13_k136_metaclass_int.py`, `g13_k137_dup_base.py`, `g13_k138_two_slots_bases.py`, `g13_k139_in_nested_def.py`, `g13_k140_in_unclaimed_callee.py`, `g13_k141_in_branch.py`, `g13_k144_slots_classvar_in_f_used.py`, `g13_k145_realistic_local_record.py`, `g13_k147_enum_intenum_str.py`, `g7_i733_class_in_function_bool_base.py`, `g7_i734_dataclass_in_function_mutable_default.py`, `g7_i736_class_in_method_slots_conflict.py`, `g7_i737_enum_in_function_dup.py`, `g7_i738_namedtuple_in_function_order.py`.

Driver repro: 17/17 family exemplars (scratchpad/rt38/verify/, F8 without --import-path) rc=0 Verification SUCCESS on main a9eac4a08 at 2026-10-29T14:55Z, each violating under CPython (scratchpad/rt38/driver-repro.txt).

```
F7 CLASS STATEMENT EXECUTED INSIDE A FUNCTION BODY: route #461 creates (with CPython's machinery) only the classes of the module top level and of the class bodies it reaches; a `class` statement inside a claimed def, a nested def, an un-claimed callee, a method or an `if` arm is lowered as a record type with no creation check, so a local class CPython REJECTS (bool base, int+str layout, two __slots__ bases, duplicate base, MRO conflict, dataclass mutable default / frozen-from-non-frozen / order+__lt__ / field() without annotation, NamedTuple order / _x, Enum duplicate / extension / IntEnum non-int, unknown class keyword, metaclass=5, __init_subclass__ raising, total_ordering without ordering) proves (TypeError / ValueError when f runs) (18)
  EXEMPLAR: g13/k145_realistic_local_record.py (`#@ no_exception \all` f defines `@dataclass class Acc: items: List[int] = []; total: int = 0` and returns `Acc().total + n`) ; g7/i733 (`class Z(bool): pass` inside f)
  CPYTHON: ValueError: mutable default <class 'list'> for field items is not allowed / TypeError: type 'bool' is not an acceptable base type -- raised every time f runs
  WHY IT PROVES: route #461's creation check walks the module top level and the class bodies it reaches; a class statement inside a function body is lowered as a record type like a module class but is never created on a synthesized namespace (18 of 20 shapes PROVE incl. a class in a nested def, an un-claimed callee and an `if` arm; k132 / k133 / k143 / k148 / k149 refused by other routes).
  PROPOSED SYSTEMATIC REPAIR: Apply #461's creation step to EVERY class statement of the file, wherever it is nested: run the class's decorators / bases / keywords / body through the same m1 interpreter (its free names resolved to the enclosing function's parameters as UNKNOWN, so any class whose creation depends on a run-time value is refused), create it with types.new_class and require the C3 order; refuse (PYCSL-R461-IMPORT-RAISES's sibling, e.g. PYCSL-R461-LOCAL-CLASS-RAISES) under any claim of a def that may execute it (the #460 reached closure). Witnesses k130-k147 + i733-i738; control: a local plain class / dataclass with default_factory (PASS).
  PROBES: g13/k130_int_str_layout.py g13/k131_namedtuple_underscore.py g13/k134_enum_extend.py g13/k135_unknown_class_kw.py g13/k136_metaclass_int.py g13/k137_dup_base.py g13/k138_two_slots_bases.py g13/k139_in_nested_def.py g13/k140_in_unclaimed_callee.py g13/k141_in_branch.py g13/k144_slots_classvar_in_f_used.py g13/k145_realistic_local_record.py g13/k147_enum_intenum_str.py g7/i733_class_in_function_bool_base.py g7/i734_dataclass_in_function_mutable_default.py g7/i736_class_in_method_slots_conflict.py g7/i737_enum_in_function_dup.py g7/i738_namedtuple_in_function_order.py
```

## REPAIR (executor x2, driver run #3, 2026-10-29, off daf5c3d1f; annotations §7.293, translational §T.6.303)

Inside m1's #461 block (gate `_rc444`, as #461). Every class statement whose nearest enclosing scope is a function
(a claimed def, a nested def, an un-claimed callee, a method, any arm inside them) is a JOB, run after the module top
level by the same statement machine on the module's FINAL bindings: its decorators / bases / keywords / body are
evaluated, the class is created by `types.new_class` and decorated for real, and `_mro363` must exist. UNKNOWN in a
job: every name an enclosing function binds (parameters, locals, nested defs / classes, imports, handler / match
names, `global` / `nonlocal` names), every name any function of the file declares `global`, and a module value of a
mutable type (list / dict / set / bytearray / an instance of a file class); a class whose creation depends on one is
refused (a bare unknown name is only stored). ONE NARROW ROW (measured: the first cut refused corpus PASS 5590): a
class `B` created by an earlier job of the same def `F` may be used by a later class statement of `F` when `B`'s
statement is directly in `F`'s body, is the only binding of the name in `F`'s whole subtree, the name is `global` in
no function, the later class sits in a LATER statement of `F`'s body, and no def in between re-binds the name.
Refusal `PYCSL-R471-LOCAL-CLASS-RAISES` (names the def the class runs in).

Witnesses 7356-7368 (k130 k131 k135 k136 k139 k140 k141 k144 k145 i733 i734 i737 i738; all 18 of `witnesses-r471/`
measured REFUSED, k134 / k137 / k138 by CPython's own verdict through the narrow row). Control 7372 (a plain local
class and a subclass of it, a local dataclass / Enum / NamedTuple / `Exception` subclass, `__slots__` over a module
base, a class in an `if` arm and in a method): PROVED at base and candidate. Advice probes `witnesses-r471/advice/`
(`int` for `bool`; the dataclass moved to module level with `field(default_factory=list)`).

OVER-REFUSAL COST, measured (candidate vs base emission of main daf5c3d1f = 33f7ac681's): byte-diff root 2604 -> 2608 .mlw, 0 MOVED / 0 GONE / 0 APPEARED (4 new controls); pyref 2186 / 2186 0/0/0; mirror 53 / 53 0/0/0 (no OWED proof). Static screens: CPython `compile()` + cookie decode of all 6937 corpus / pyref / mirror / pycsl_lib files: only the 12 new #465 witnesses fail; 1274 claimed files scanned for function-body classes, module-dunder reads and dunder attribute reads -- the one PASS file the first cut refused (5590, `class C(B)` over a class `B` of the same def) is admitted by the narrow row below; 0 corpus PASS file refused.


## GATES (routes #465 / #469 / #470 / #471 together, worktree pycsl-x2 off daf5c3d1f, 2026-10-29)
Fidelity: check-self-annotate-sync rc=0 (938 verbatim), self-annotate-mirror-check rc=0 (53). Byte-diff vs
`scratchpad/v13/ca` (emission of 33f7ac681, docs-only since): root 2604 -> 2608 0 MOVED / 0 GONE / 0 APPEARED (4 new
controls); pyref 2186 / 2186 0/0/0; mirror vs `v13/ma` 53 / 53 0/0/0 (no OWED proof). Soundness planes: first run 1 of 61
RED -- check-dropped-mutation CTXBIND 52 > 51, the compile gate's own `with open(..) as` (DIAGNOSED: a new `with ... as`
binding in the scanned emitter; repaired by `pathlib.Path(..).read_bytes()`, not by moving the ratchet), re-run
run-soundness-planes rc=0, 61 / 61 green. Ledgers: trusted-reasons rc=0 (409 <-> 409), assumed-facts --emit-dir rc=0, refusal-witness-coverage rc=0
(365 demonstrated, census +39 rows via `_census_row`), refusal-advice-audited rc=0 (191 / 254, R465 FOLLOWABLE),
dropped-mutation rc=0 (51 ctxbind), getattr-erasure rc=0, open-route-carriers rc=0, trusted-frame-honesty rc=0,
trusted-raises-honesty rc=0, clause-survival --emit-dir rc=0 (10 ledgered), stdlib-modules-verify rc=0, doc-coherency
rc=0. `\trusted` lines 437 (= base). Candidate: 39 witnesses REFUSED, 4 controls + 4 advice probes Verification
SUCCESS. Base daf5c3d1f: 18 sampled witnesses (7330 7333 7336 7341 7342 7343 7344 7345 7349 7350 7351 7355 7356 7360
7361 7364 7365 7367) and the 4 controls Verification SUCCESS. Compile screen (CPython `compile` + cookie decode) of 6937
corpus / pyref / mirror / pycsl_lib files: 12 failures, all the new #465 witnesses; 99 files carry a SyntaxWarning
(refusing warnings would cost them).

## RESIDUALS
- A job judges the class whether or not the def can reach it (sound, over-approximate: a class in a def no claimed
  def calls is judged too; measured 0 PASS refused).
- A module value mutated at run time through an attribute / item store on an immutable-typed object, or a module
  attribute rebound from ANOTHER module, is taken at its final top-level value.
- Names bound only in the `if __name__ == "__main__":` block are unbound for a job (refused if used).
