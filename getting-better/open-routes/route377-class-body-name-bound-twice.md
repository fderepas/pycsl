# OPEN ROUTE #377 — A NAME BOUND TWICE IN A CLASS BODY: pycsl USES THE FIRST `def`, CPython RUNS THE LAST
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r377 executor off b815ee8d8 — sound refusal, see REPAIR; shared with #377-#380). Was OPEN, Severity 1.** Red-team round 29 (2026-10-25, probes around the #226 increment and #369-#372); driver-reproduced on main 919533395 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt29/driver-repro.txt`).
Witnesses `witnesses-r377/`: `a50_init_defined_twice.py`, `a58_method_twice_caller.py`, `a62_init_twice_invariant_param.py`.

The constructor goal and call-site contracts are taken from the first `def` of a name in a class body; CPython keeps the last binding. a50: goal `n = 7 -> n >= 5` from a dead `__init__` (CPython 0); a62: a dead `__init__`'s `#@ requires x >= 0` becomes the goal premise (CPython -3); a58: `c.get()` uses the first def's `ensures result = 1` while the emitted body is the last def (CPython 2). Route #118's duplicate-def check covers module scope only (module-level a57 FAILs correctly).

Repair: Extend #118 to class scopes: refuse a name bound twice in a class body (or resolve the last binding everywhere).

## REPAIR (2026-10-25, r377 executor off b815ee8d8; code 718bb669 / 13ee6e9e / 47fed51b, corpus 91dc9137 / 7b794661 / 4f3a5cfc, docs 91dc9137 (annotations §7.38 / translational §T.6.49), census 7b794661, route docs)
**Design (shared by #377-#380): sound refusals, no emission change, no new def, ledger 3.** #377 / #378 extend the class-scope
walk of routes #122 / #130 in `Module3_Weaver.process` (shared by the file and dependency pipelines, mirror twin `\trusted`; it
appends to the existing "a name's runtime binding is not the `def` the model resolves it to" raise — no new raise site). #379 /
#380 extend #369's inline arity block in `_run_pipeline` (mirror twin `\trusted`): two NEW codes `PYCSL-R379-STARRED-CALL-ARGUMENT`
and `PYCSL-R380-METACLASS-CALL`; the `init=False` / `super().__init__` / `C.__init__(self, ..)` arity reuses
`PYCSL-R369-CONSTRUCTOR-ARITY` (message unchanged, so #369's census rows still match).
RULES. (#377 / #378) in every CLASS body, a name with >= 2 binding sites (defs, stores, imports, except-as / match captures;
nested function / lambda bodies excluded) of which one is a `def` / `class` or an ANNOTATED member is REFUSED, except a property
accessor chain (`@property def x` then only `@x.setter` / `.getter` / `.deleter` defs — itself still refused by the decorator rule
at base, measured) and an `@overload` chain (stubs before the implementation; the stubs' `ensures` already bind the
implementation, stub `assigns` / `requires` are refused by the overload model, measured). (#379) in a non-`\trusted` /
non-`\abstract` function, a call with a `*` / `**` argument of a file class, a module-level `def`, or a method name of a file
class (receiver not an imported / file-unbound name) is REFUSED, except a `*xs` landing entirely in the `*args` of every
candidate whose contract does not name that parameter (the mirror's `self.set_precedence(p, n, *node.ifs)`). (#380) §T.6.46's
constructor walk continues past `@dataclass(init=False)` (to `object.__init__`); `super().__init__(..)` / `super(X, self)` is
arity-checked against the class after X in the MRO of X and of each file subclass whose MRO tail is that class's own MRO
(`object.__init__` at the end); `C.__init__(self, ..)` against C's constructor; a construction through a `metaclass=` other than
`type` / `abc.ABCMeta` / a file metaclass binding no `__call__` on its MRO is REFUSED.
**Probe table** (full pycsl proof via heavy.sh; base = b815ee8d8 worktree; corpus copies 5140-5159 / 5170-5174):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| a50 two `def __init__` | 5140 | invariant violated (0) | rc=0 PROVED | rc=1 REFUSED (class-body binding, #377) |
| a58 two `def get` | 5141 | 2 | rc=0 PROVED | rc=1 REFUSED (#377) |
| a62 dead `__init__`'s `requires` | 5142 | -3 | rc=0 PROVED | rc=1 REFUSED (#377) |
| a47 `field(default=3)` then `n = -1` | 5143 | -1 | rc=0 PROVED | rc=1 REFUSED (#378) |
| a48 field annotated twice | 5144 | -1 | rc=0 PROVED | rc=1 REFUSED (#378) |
| b02 `D(**kw)` unknown key, no_exception | 5145 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R379-STARRED-CALL-ARGUMENT |
| b25 `C(**{"y": 1})` | 5146 | TypeError | rc=0 PROVED | rc=1 REFUSED R379 |
| b26 `D(1, **{"x": 2})` | 5147 | TypeError | rc=0 PROVED | rc=1 REFUSED R379 |
| b27 `D(**kw).x == 0` | 5148 | 5 | rc=0 PROVED | rc=1 REFUSED R379 |
| b47 `D(**{"x": 5}).x == 0` | 5149 | 5 | rc=0 PROVED | rc=1 REFUSED R379 |
| b48 `C(**kw).x == 0` | 5150 | 5 | rc=0 PROVED | rc=1 REFUSED R379 |
| b50 `D(**kw)`, `kw: Dict` | 5151 | 3 / TypeError | rc=0 PROVED | rc=1 REFUSED R379 |
| b52 `D(1, **kw).y == 0` | 5152 | 7 | rc=0 PROVED | rc=1 REFUSED R379 |
| b57 `h(1, **kw)`, no_exception | 5153 | TypeError | rc=0 PROVED | rc=1 REFUSED R379 |
| b14 `@dataclass(init=False)`, `D(1)` | 5154 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R369-CONSTRUCTOR-ARITY |
| b20 `super().__init__(y=1)` | 5155 | TypeError | rc=0 PROVED | rc=1 REFUSED R369-CONSTRUCTOR-ARITY |
| b29 metaclass `__call__` returns 42 | 5156 | AttributeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R380-METACLASS-CALL |
| b31 `init=False`, required field, `D(1)` | 5157 | TypeError | rc=0 PROVED | rc=1 REFUSED R369-CONSTRUCTOR-ARITY |
| NEW latent: `super().__init__(5)` over `__init__(self)` | 5158 | TypeError | rc=0 PROVED | rc=1 REFUSED R369-CONSTRUCTOR-ARITY |
| NEW latent: `super().__init__(5)` over `object` | 5159 | TypeError | rc=0 PROVED | rc=1 REFUSED R369-CONSTRUCTOR-ARITY |
| control: `init=False`, `D().x == 4` | 5170 | 4 | rc=0 PROVED | rc=0 PROVED |
| control: metaclass without `__call__` | 5171 | 1 | rc=0 PROVED | rc=0 PROVED |
| control: `super().__init__(k + 100)` | 5172 | 107 | rc=0 PROVED | rc=0 PROVED |
| control: `@overload` chain in a class | 5173 | 1 | rc=0 PROVED | rc=0 PROVED |
| control: distinct method names | 5174 | 5 | rc=0 PROVED | rc=0 PROVED |
Other probes (scratchpad, not filed): `*xs` into a non-`*args` def / `c.get(**{..})` / `B.__init__(self, 1, 2)` were already
FAIL / refused at base and are REFUSED after; `*ys` into an uncontracted `*xs` (admitted) stays a fail-closed WhyML type error at
both; `class C: K = 1; K = 2` (no def / annotation) is FAIL at base (not refused, honest); an assignment-then-`def` and a dataclass
`n -= 5` were already refused by route #132.
**Census / blast radius.** Before landing (both corpora, 53 mirrors, `pycsl_lib`, live `src/pycsl` as a mirror dependency): 3
class bodies bind a name twice (1323, 1355, 1371 — expected-FAIL witnesses already refused); 0 `metaclass=` with `__call__` (2
pyref metaclasses, none constructed through `__call__`); 3 `@dataclass(init=False)` (1461-1463, constructor inherited — still
admitted); 50 `super().__init__` / `C.__init__` calls (all well-formed); `*` / `**` calls: 62 root sites all in `__main__` blocks
(not verified functions), 7 mirror sites (`template.format(*..)`, `self.set_precedence(.., *node.ifs)` into `*nodes` —
admitted —, `Constant(*args, **kwargs)` / `Constant.__new__(..)` on a dynamically created global — out of scope), 6 library
sites (imported callees). The first candidate mirror sweep showed 3 GONE (pure_ast: `Constant.__new__` matched the metaclass
`__new__` by attribute name — receiver rule added, 13ee6e9e; ir_resolve / frontend `__init__`: the LIVE Module 3 is a dependency
and route #275 refused my own `sorted(key=lambda ..)` — rewritten, 47fed51b). Final sweeps (code 47fed51b): root 2357 base / 2362
candidate .mlw, 0 MOVED / 0 GONE / 0 APPEARED (5 new control sources); pyref 2186 / 2186 0/0/0 (`--min-files 2000`); mirror
53 / 53 0/0/0 (`--min-files 50`) — **no OWED proof**.
**Gates** (rc): witnesses / controls above (full proof via heavy.sh, base b815ee8d8 worktree vs candidate); byte-diff-compare root rc=0, pyref rc=0, mirror rc=0 (above); check-self-annotate-sync.sh rc=0 (926 verbatim); self-annotate-mirror-check.sh rc=0 (53); run-soundness-planes.sh fast **61/61** rc=0 (first run RED on check-claim-vacuity: control 5172 copied a `requires True`, dropped in 672aa0c5; `--slow` NOT run); check-getattr-erasure rc=0 (DECLARED 0); check-stdlib-modules-verify rc=0 (one command via heavy.sh: 83 VERIFY, the known 21 non-verifying); doc-coherency --check rc=0; check-assumed-facts rc=0 (85 facts, all reviewed families; ledger 3); check-dropped-mutation rc=0 (0 / 51 / 5 / 0); check-refusal-witness-coverage rc=0 (306 demonstrated / 5 undemonstrated = ceiling 5; the 2 new raise sites demonstrated by rows 5145-5153 / 5156; rows 5140-5159 via `_census_row`); check-trusted-reasons rc=0 (420 / 420, ratchet 259); check-trusted-raises-honesty rc=0 (19 / 61, ratchet 61); check-assigns-underdeclaration --transitive rc=0 (TRAP 3, HOLE 0); check-mirror-coverage rc=0 (549 / 41).
**Residuals.** (1) Module scope: a name bound twice at module level is unchanged (duplicate `def` fail-closed, rebinding refused by
#118). (2) `*` / `**` at calls of IMPORTED functions / classes, builtins and `cls(..)` are not checked (the lowering's own #232 /
#275 rules apply there). (3) `super().__init__` whose MRO tail differs from the next class's own MRO (diamonds), a `__new__`
anywhere, and an imported next class are not arity-checked. (4) A metaclass inherited from an imported base class (no
`metaclass=` keyword in the file) is not seen. (5) Over-refusal: a `*`/`**` forwarding wrapper of a file function (0 census
users), and a method name shared with an unrelated file class's `*args`-less method.
