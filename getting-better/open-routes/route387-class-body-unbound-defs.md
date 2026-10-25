# OPEN ROUTE #387 — CLASS-BODY DEFS CPython NEVER BINDS AS ATTRIBUTES
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r386 executor off 5addbdeef — sound refusal, see REPAIR; shared with #386). Was OPEN, Severity 1.** Red-team round 30 (2026-10-25, probes around #373-#380 and route #226 increment 2c); driver-reproduced on main a064a298f (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt30/driver-repro.txt`).
Witnesses `witnesses-r387/`: `h07_class_body_global_decl.py`, `h10_class_body_if_false_def.py`, `h21_class_body_while_false_def.py`, `h22_global_init_decl.py`, `h24_if_version_def.py`, `h25_class_body_try_def_raises.py`, `h26_global_method_decl_invariant.py`.

`global get` / `global __init__` in a class body, a def under `if False:` / `while False:` / `if sys.version_info < (3, 0):`, or after a raise inside `try`: one binding site each, so #377's bound-twice rule never fires; the def is modelled as a method. CPython AttributeError.

Repair: Module 3: refuse `global` / `nonlocal` in a class body naming a member; refuse (or treat as possibly unbound) any def / class / annotated member nested under a compound statement in a class body.

## REPAIR (2026-10-25, r386 executor off 5addbdeef, repaired with route #386; code 13fbfa1ed + 20ccfe42d, corpus ebed9c6e7 + 20ccfe42d, docs 475527100 + 20ccfe42d (annotations §7.41 / translational §T.6.52), census d3fffd4f9, route docs)
**Design: sound refusal in route #377's class-scope walk of `Module3_Weaver.process` (routes #122 / #130; mirror twin `\trusted`),
appended to the existing "a name's runtime binding is not the `def` the model resolves it to" raise — no new raise site, no new
def, no emission change, ledger 3.** RULES: in every CLASS body (walk not entering nested def / class / lambda bodies), (a) a
`global` / `nonlocal` statement naming a name the body binds is REFUSED; (b) a `def` / `class` / annotated member reached through
an `if` / `while` / `for` / `try` / `with` / `match` (incl. async / `try*`) is REFUSED — whether it runs is not modelled — unless
every compound statement on the way is an `if True:` and the path enters its BODY (control 4940; its `else` arm is refused).
**Probe table** (full pycsl proof via heavy.sh; base = 5addbdeef worktree; corpus copies 5300-5310 / 5322 / 5323 / 5325):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| h07 `global get` before `def get` | 5300 | AttributeError | rc=0 PROVED | rc=1 REFUSED (route #387) |
| h10 `def get` under `if False:` | 5301 | AttributeError | rc=0 PROVED | rc=1 REFUSED |
| h21 `def get` under `while False:` | 5302 | AttributeError | rc=0 PROVED | rc=1 REFUSED |
| h22 `global __init__` (invariant + no_exception) | 5303 | AttributeError | rc=0 PROVED | rc=1 REFUSED |
| h24 `def get` under `if sys.version_info < (3, 0):` | 5304 | AttributeError | rc=0 PROVED | rc=1 REFUSED |
| h25 `def get` after `raise` in `try:` | 5305 | AttributeError | rc=0 PROVED | rc=1 REFUSED |
| h26 `global get` at the top, caller no_exception | 5306 | AttributeError | rc=0 PROVED | rc=1 REFUSED |
| q07 annotated `K: int = 5` under `if False:` | 5307 | AttributeError | rc=1 FAIL | rc=1 REFUSED |
| NEW latent q08 `def get` under `for _i in range(0):` | 5308 | AttributeError | rc=0 PROVED | rc=1 REFUSED |
| q10 `nonlocal get` in a function-local class | 5309 | AttributeError | rc=1 REFUSED (ir-semantic) | rc=1 REFUSED |
| NEW latent q11 `def get` in the `else` of `if True:` | 5310 | AttributeError | rc=0 PROVED | rc=1 REFUSED |
| control: plain class-body members | 5322 | 1 | rc=0 PROVED | rc=0 PROVED |
| control: `if True:` inside a METHOD | 5323 | 1 | rc=0 PROVED | rc=0 PROVED |
| control: `def get` in the body of a class-body `if True:` | 5325 | 1 | rc=0 PROVED | rc=0 PROVED |
| control (existing): 4940 `__eq__` under `if True:` | 4940 | ok | emits | byte-IDENTICAL |
**Census / blast radius.** Before landing (both corpora, 53 mirrors, `pycsl_lib`, live `src/pycsl` as a mirror dependency):
#386 — a def / class nested in a function and named like a builtin AND read: 1 (3784's local `class KeyError`, expected FAIL,
already refused by route #305); imports binding a builtin name: `pycsl_lib/re` (`from ._engine import compile`, never read —
admitted), 1374 / 3789 (`from builtins import ..`, route #131's own arm); lambda parameters / comprehension targets named like a
builtin and read: 0; method-level `def next` (pure_ast) and module-level user `def len` / `ord` / `min` (route #75's 1182-1187)
are class / module scope and unchanged. #387 — class-body `global` / `nonlocal`: 0; members under a class-body compound
statement: 1355 (route #122, refused), 4821 (refused by PYCSL-SEM-OVERRIDE-REFINEMENT), and control 4940 (`__eq__` under
`if True:`) — the FIRST candidate sweep GONE'd 4940, so the body of a literal `if True:` is admitted (20ccfe42d); no
`if TYPE_CHECKING:` member. Final sweeps (code 20ccfe42d): root 2405 base / 2411 candidate .mlw, **0 MOVED / 0 GONE / 0 APPEARED**
(6 new control sources emit, 21 new witnesses refuse); pyref 2186 / 2186 0/0/0 (`--min-files 2000`); mirror 53 / 53 0/0/0
(`--min-files 50`) — **no mirror mover, no OWED whole-file proof**.
**Gates** (rc, one run for routes #386 / #387 on the final tree; logs in the executor scratchpad `r386/g/`): witnesses / controls
above (full proof via heavy.sh, base 5addbdeef worktree vs candidate); byte-diff-compare root rc=0, pyref rc=0, mirror rc=0
(above); check-self-annotate-sync.sh rc=0 (926 verbatim); self-annotate-mirror-check.sh rc=0 (53); run-soundness-planes.sh fast
**61/61** rc=0 (`--slow` NOT run); check-getattr-erasure rc=0 (DECLARED 0; ABSENT 10 / UNKNOWN 43 unchanged); check-stdlib-modules-verify rc=0 (83 VERIFY, the known 21 non-verifying) (one command via heavy.sh);
doc-coherency --check rc=0; check-assumed-facts rc=0 (85 facts, all reviewed families; ledger 3); check-dropped-mutation rc=0 (0 / 51 / 5 / 0);
check-refusal-witness-coverage rc=0 (310 demonstrated / 5 undemonstrated = ceiling 5; no new raise site; rows 5290-5310 via
`_census_row`); check-trusted-reasons rc=0 (420 / 420, ratchet 259); check-trusted-raises-honesty rc=0 (19 / 61, ratchet 61);
check-assigns-underdeclaration --transitive rc=0 (TRAP 3, HOLE 0).
**Residuals.** (1) Over-refusal: a class-body member under a condition that is always true but not the literal `True`
(`if TYPE_CHECKING:`, `if sys.version_info >= (3, 0):`, `try:` without a raise) — 0 census users. (2) Module scope is
unchanged (a module-level def under `if False:` / `global` inside functions is route #122's / #118's model). (3) `global x` in a
class body naming a name the body does NOT bind is admitted (it changes no class attribute).
