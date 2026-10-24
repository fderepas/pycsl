# OPEN ROUTE #339 — ENUM MEMBERS ARE MODELLED AS PLAIN INTS (arithmetic/ordering on plain Enum; user __eq__/__lt__ ignored)
**Status: REPAIRED, candidate (gen #37, 2026-10-24; opened the same day), Severity 1.** Red-team round 24; driver-reproduced on main (rc=0; CPython violates).
Witnesses `witnesses-r339/`: `C.A` lowers to `get_A _class_c : int` and #325 classes it int (int-literal value). Plain Enum: `x - x`, `x < x`, `-x + x`,
`x * x`, `a[x]` raise TypeError in CPython but `no_exception \all` + value claims prove (d26, d27, d31, e12, e13, e14). User `__eq__`/`__lt__` on Enum/IntEnum
are emitted but ignored: `x == x` proves True while CPython's __eq__ returns False (d17, d18, d19). Not BUILTIN-EXACT (static type is the user class).
Repair: Enum members are opaque values of an abstract per-enum type (no int arithmetic/ordering for plain Enum; IntEnum/IntFlag members may
keep int semantics only when no user dunder overrides the operator); operators on enum members dispatch to user dunders or are refused.

## REPAIR (2026-10-24, r339 executor off 5e517ffc; code 148ebcaa, corpus adea2535, docs 0b3e2c03, census 9b14185e)
**Design: sound refusal of every non-identity use of an OPAQUE enum member; int semantics kept only for a dunder-free
`IntEnum`/`IntFlag`.** One inline block in `_run_pipeline` beside route #273's definition-time block (mirror twin `\trusted`;
no new def, no lambda; no emission change; ledger 3). An abstract per-enum WhyML type was measured unnecessary: the
refusal leaves every admitted use (binding, `==`/`is`, `.value`/`.name`, enum-annotated parameter / return) on the
existing lowering, where it is already faithful or merely imprecise (`get_A _class_c` is an unconstrained `val`, so
`C.A == C.B` is unprovable either way). CENSUS before landing (CPython `ast`): pycsl-reference 1 enum class (4243,
`Color.RED.value` — `.value` admitted; still refused by route #325), the self-annotate mirror's `pure_ast._Precedence`
(an `IntEnum` with no dunder: transparent, untouched), python-reference / `pycsl_lib` 0. Annotations §7.26 (1),
translational §T.6.37.
RULE (`PYCSL-SEM-ENUM-MEMBER-OPERATION`): a class with a base (name or attribute tail) in `Enum`/`IntEnum`/`Flag`/`IntFlag`/
`StrEnum`/`ReprEnum` or another enum of the file is an enum; it is TRANSPARENT iff int-like (`IntEnum`/`IntFlag`/`int`
base chain) and it (with its enum bases) defines no dunder other than `__init__`/`__new__`/`__init_subclass__`/attribute
dunders. For every OPAQUE enum, a member expression (`C.M`, `C(v)`, `C[k]`, a name bound to one — fixpoint over
assignment / walrus / `for` over `C` / module bindings —, a parameter / field / callee result annotated `C`/`"C"`/
`Optional[C]`/`C | None`) is admitted only as: a name-target assignment value; an operand of `is`/`is not`, or of
`==`/`!=`/left of `in`/`not in`/`match` when no `__eq__`/`__ne__` is user-defined; a truth test when no `__bool__`/
`__len__`; `.value`/`.name`; an expression statement; a return / argument / default where the annotation is the enum;
`isinstance`/`id`/`type` (`hash` without `__hash__`). Everything else — arithmetic, unary `-`/`+`/`~`, ordering,
indexing, augmented store, container elements or a container annotation, builtins / str conversion, an `int` parameter,
the class object as an argument (`list(C)`) — is refused.

**Probe table** (full pycsl proof via heavy.sh; base = 5e517ffc worktree; CPython 1 = the `__main__` assertion fails):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| d17 `IntEnum` + user `__eq__` -> False, `x == x` proved True | 4590 | violates | rc=0 PROVED | rc=1 REFUSED |
| d18 plain `Enum` + user `__eq__`, `x == x` | 4591 | violates | rc=0 PROVED | rc=1 REFUSED |
| d19 `IntEnum` + user `__lt__` -> True, `x < x` proved False | 4592 | violates | rc=0 PROVED | rc=1 REFUSED |
| d26 plain `x < x`, `no_exception \all` | 4593 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| d27 plain `x - x` | 4594 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| d31 plain `x * 0` | 4595 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| e12 plain `-x + x` | 4596 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| e13 plain `a[x]` (via `x == x * 0`) | 4597 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| e14 plain `x * x >= 0` | 4598 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| NEW latent: plain member passed to an `int` parameter, callee `v - v` under `no_exception \all` | 4599 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| control: plain member bound / aliased / `==` / `.value` | 4600 | ok | rc=0 | rc=0 PROVED |
| control: dunder-free `IntEnum` `x - x == 0` under `no_exception \all` | 4601 | ok | rc=0 | rc=0 PROVED |
Extra shapes probed (scratch, not corpus; refused after, already non-proving at base for other reasons): enum-annotated
parameter `k - k`, `self.kind - self.kind` on a `kind: C` field, `for m in C: m - m`, `Flag` member `+ 2`, `IntEnum` with a
user `__add__`.
**Blast radius**: root 2244 base / 2247 candidate 0 MOVED / 0 GONE / 0 APPEARED (3 new controls); pyref 2186/2186 0/0/0;
mirror-emit-sweep 53/53 0/0/0 (`--min-files 50`) — no OWED proof, no mirror file GONE. One latent false proof found (4599).
**Gates** (shared with route #340, one run): see route #340.
**Residuals.** (1) Contract expressions (`#@ ensures \result - C.A == 0`) are not walked by this AST check (they are not
Python AST); an enum member's arithmetic inside a contract is still modelled as int. (2) Flow beyond the tracked forms
(an enum stored through `setattr`, `getattr`, a dict/list built outside a verified function, a non-annotated method
result) is not seen. (3) Enum classes reached through an import of another user module are not resolved (per-file
check). (4) Over-refusal: a plain member as an element of a container, in an f-string or `print`, or a transparent
`IntEnum` with only a `__str__`/`__repr__` override, is refused (0 users measured).
