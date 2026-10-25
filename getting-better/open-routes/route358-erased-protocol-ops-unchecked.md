# OPEN ROUTE #358 — PROTOCOL OPERATIONS ON ERASED VALUES HAVE NO EXCEPTION CHECK
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r357 executor off 1a9cfa42 — see REPAIR). Was OPEN, Severity 1.** Red-team round 26 (2026-10-25, probes around the #339/#340/#343-#345 repairs); driver-reproduced on main 3d937bdb (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt26/driver-repro.txt`).
Witnesses `witnesses-r358/`: `r07_for_over_self.py`, `r11_self_missing_attr.py`, `r14_bool_len_negative.py`, `r19_join_self.py`, `r24_object_for.py`, `r25_object_attr.py`, `r32_any_attr.py`, `r46_not_self_len.py`, `r51_self_attr_eq.py`.

Under no_exception: `for z in self` / `for z in x` (`x: object`) go through `iter_length`/`iter_get` (r07, r24: TypeError); a missing `self.zz` or `x.foo` on `object` / `Any` is an opaque read (r11, r51, r25, r32: AttributeError); `if self` / `not self` lower to `self <> 0` and never call `__len__` (r14, r46: ValueError for `__len__ -> -1`); `"".join([self])` is not in R343's builtin list (r19: TypeError).

Repair: Extend R343's failing assertion beyond builtin names: iteration / comprehension over an erased value, loads of attributes not known as fields on an erased base, truth tests on an erased receiver (the `x: object` truth test already fails, r45), str/list methods with erased arguments.

## REPAIR (2026-10-25, r357 executor off 1a9cfa42, repaired with routes #357 / #359; code fb898973 / af97b85a, corpus + docs 570c626f (annotations §7.31, translational §T.6.42), census 66f2dd33)
**Design: route #343's failing assertion, extended to the protocol operations.** Under `no_exception` (any set or `\all`),
program context, with a non-empty route #249 scope, and when route #251's `r251_erased?` probe calls the operand erased, the
lowering is preceded by `assert { [@expl:PyCSL-R358 ..] false }` at four inline sites (all mirror twins `\trusted`, no new def,
no new self field — re-entry is marked on the IR dict, `_pycsl_r358n`, stripped on entry, like route #311's marker):
`_classify_iterable` (the two opaque `iter_length` bounds of a `for`); `_to_bool` (every truth test: `if` / `while` / `not` /
`and` / `or` / conditional expression); `_expr_to_whyml` after the typed fast paths, for (a) a `FieldGet` / `Attribute` whose
attribute is not KNOWN on the erased base — `dir(object)`, plus, for a base whose declared class is a file class, its methods
and the names its methods store on `self` (`nonrecord335` is popped by `ir_resolve` before Module 6, so a class-body constant
of a field-less class is not known: fail-closed), (b) a comprehension / generator over an erased iterable, (c) a `str` /
`list` / `dict` / `set` / `tuple` / `bytes` method (literal receiver, or a dotted name of that symbol type) handed an erased
argument or element (`append`, and `insert`'s element, exempt). A VC label, not a refusal: no census site.
**Probe table** (full proof via heavy.sh; base = 1a9cfa42):
| witness | corpus | base | after |
|---|---|---|---|
| r07 `for z in self` | 4807 | rc=0 PROVED | rc=1 FAIL (PyCSL-R358 iteration) |
| r11 `self.zz` | 4808 | rc=0 PROVED | rc=1 FAIL (PyCSL-R358 attribute) |
| r14 `if self:`, `__len__` -> -1 | 4809 | rc=0 PROVED | rc=1 FAIL (PyCSL-R358 truth test) |
| r19 `"".join([self])` | 4810 | rc=0 PROVED | rc=1 FAIL (PyCSL-R358 str method) |
| r24 `for z in x`, `x: object` | 4811 | rc=0 PROVED | rc=1 FAIL (PyCSL-R358) |
| r25 `x.foo`, `x: object` | 4812 | rc=0 PROVED | rc=1 FAIL (PyCSL-R358) |
| r32 `x.foo`, `x: Any` | 4813 | rc=0 PROVED | rc=1 FAIL (PyCSL-R358) |
| r46 `not self` | 4814 | rc=0 PROVED | rc=1 FAIL (PyCSL-R358) |
| r51 `y = self.zz; y - y` | 4815 | rc=0 PROVED | rc=1 FAIL (PyCSL-R358) |
| NEW latent: `1 if self else 0` | 4824 | rc=0 PROVED | rc=1 FAIL (PyCSL-R358 truth test) |
| NEW latent: `mk().foo`, `mk() -> Any` | 4825 | rc=0 PROVED | rc=1 FAIL (PyCSL-R358 attribute) |
| NEW latent: `s.startswith(x)`, `x: Any` | 4826 | rc=0 PROVED | rc=1 FAIL (PyCSL-R358 str method) |
| shape: `xs.count(self)`, raising `__eq__` | 4827 | rc=1 FAIL (`__eq__` raise analysis) | rc=1 FAIL (PyCSL-R358 list method) |
| control: record field read, `for` over `List[int]`, truth of `int` / `str` / `List[int]`, `"".join` of strings, `self.h()`, no_exception | 4831 | rc=0 PROVED | rc=0 PROVED |
A comprehension over an erased value (red-team r47; `[1 for z in x]`, `x: object`) FAILED at base already (Why3 type error:
the comprehension wants an array); it now also carries the R358 assertion.
**Blast radius**: the shared sweep in route #357's REPAIR — root 0 MOVED (no corpus file has one of these operations on an erased
value under `no_exception`), pyref 0/0/0, mirror 53/53 0/0/0 (the mirror declares no `no_exception`).
**Gates**: see the shared gate list in route #359's REPAIR.
**Residuals.** (1) Class-body constants / properties of a field-less class read through an erased receiver FAIL under
`no_exception` (over-approximation; the resolved IR does not carry the class body). (2) Methods of a builtin receiver held in a
local whose symbol type is not recorded (e.g. a `List` built by a call) are not checked; `xs.append(x)` and the `insert`
element are exempt by design (they store without dispatch). (3) Outside `no_exception` these operations stay opaque
(exceptions are ambient there, as before).
