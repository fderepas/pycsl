# OPEN ROUTE #325 — EVERY UNMODELLED VALUE FALLS BACK TO AN OPAQUE `int` (whatever its Python type): int-only laws are proved of floats, strings, lists
**Status: REPAIRED (gen #37, 2026-10-24; candidate, see REPAIR), was OPEN (2026-10-24), Severity 1.** Red-team round 19; driver-reproduced on main (rc=0; CPython violates).
Root cause: the fallbacks `val constant f : int`, `get_X (m) : int`, `getattr_c`, `subscript_get`, and unmodelled calls `val m_f_0 (..) : int`
type an unknown value as INT, so `x % 1 == 0`, `int(x) == x`, `x * 0 == 0`, `x < E or x == E or x >= E+1` are provable of floats/strings/lists.
#322's name-keyed refusal of math/cmath/sys float constants is one symptom and is bypassable (F1). Witnesses `witnesses-r325/` (+ helper consts19.py):
- F1 (#322 bypasses): re-export `consts19.PI` (p01) / `from consts19 import PI` (p02), `importlib.import_module("math").pi` (p03),
  `__import__("math").pi` (p04), `m = math; m.pi` (p05), module-level `M = math` (p07).
- F2 (values): main-file globals `EPS = 0.5` (t06: `x < EPS or x >= EPS+1 or x == EPS` proved, CPython False at x=1), `F = 0.5` (r05),
  annotated `F: float = 0.5` still int (r12), `X = mk()` list (r13), `int(F) == F` with F=2.5 (t03); class attrs `C.R` (c01), `self.R` (c06),
  `Color.RED.value` (c05), `T[0]` of a global float tuple (c07); user-module attrs `consts19.F` (r02), `consts19.S * 0 == 0` (q02).
- F3 (calls): `time.time()` (p08), `random.random()` (q01), `os.getcwd() * 0 == 0` (q03), `float.fromhex` (q07).
FLOAT-FINITE does not cover this (floats are typed int, not real). Repair: an opaque fallback must be typed by the value's known Python type
(literal/annotation/return annotation/stub) — a non-int known type must NOT get int theory: use an abstract opaque type (or real for float
under FLOAT-FINITE) or refuse int arithmetic/comparison over it; an UNKNOWN type must not be assumed int either (refuse int laws over it, or a
fresh abstract type). Census every int-typed opaque fallback emission site; supersede/subsume the #322 name-keyed refusal.

## REPAIR (2026-10-24, r325 executor off 0da66911; commits f727109a + 4890e1d3 (code), 6562aec2 (corpus), 06382014 (census), da90b338 (docs) + route docs)
**Design (measured first).** The fallbacks are emitted at ~100 sites across Module 6 (census below), so the decision is
taken ONCE, on the EMITTED WhyML, in `_run_pipeline` just before `return _mlw` (inline, no new def; the mirror twin of
`_run_pipeline` is `\trusted`), refusing `PYCSL-R325-OPAQUE-INT-FALLBACK`. A fresh abstract type (option b, typed) was
measured out: 486 root / 1700 pyref emissions carry an unconstrained `int` val, every one would move. A plain
operator blacklist moved 51 root files but missed flows (returns, parameters, receivers). The landed rule:
- ORIGINS = unconstrained (`ensures`-free) `int` vals that stand for a MODULE-LEVEL Python value: `val constant n` for a
  name bound at module/class level in the file, an import / module alias / from-import (any free name under `from m
  import *`), a class object (`c`, `_class_c`); `getattr_<cls> x h` when `h` hashes a CLASS-LEVEL non-int attribute;
  `pycsl_getattr_*`; call stubs `<path>_<k>` of an imported / builtin callable (resolved from the source's `Call`s).
- KNOWN-INT exempt: an int expression bound at module/class level (fixpoint over literals and known names; `global`
  rebinding disqualifies), `sys.maxsize|maxunicode|hexversion|api_version`, `sys.float_info.<int field>`, `len id hash ord
  int range`, `random.randint|randrange|getrandbits`, `os.getpid|getppid`, `time.*_ns`, `math.gcd|lcm|isqrt|factorial|
  comb|perm`, a user function/method annotated `-> int|bool` whose body does not return a fallback.
- TAINT flows through `let x = e in` / `x := e`, an opaque op / getter / subscript applied to a tainted term, tuples,
  constructors and container builders (`Seq.cons`, `Array.make`), `begin..end` / `try..with` / `(let .. in u)` / if-arms,
  `raise (Return e)` and declaration tails (function tainted, its calls tainted), a USER function's parameter (taint the
  callee's parameter), and a receiver-dropped method stub `r_m_k` whose receiver `r` is tainted.
- ADMITTED positions: argument of an opaque op, RHS of a binding, return, discarded statement, one side of a PROGRAM
  `=` / `<>` (or `pycsl_py_eq`) whose other side holds no term of the same origin (route #47's per-default
  `pycsl_getattr_default_*` keeps its reflexivity). Everything else (int operator, ordering, `pycsl_mod/div`, a modelled
  function, a contract term, a reflexive compare) is refused. Binders follow WhyML scoping (`let` from its `in` to the
  enclosing group/block — `F` and `f` fold to one WhyML name, witness 4260); comments / strings / `[@...]` stripped.
- #322 SUBSUMED: with the #322 raise disabled, 4194-4198, s05, t01 (`from math import *`), t02 (`getattr`), t20, t21 all
  refuse with R325; t22 (int field) is admitted. #322 is KEPT as the first, name-keyed layer (removing it changes the
  refusal code of 4194-4198 and their census rows; it is not byte-neutral to remove).

**Census of int-typed opaque fallback emission sites (module6_whyml/)**:

| site | value kinds reaching it | status |
|---|---|---|
| `expressions.py` `val constant {safe} : int` (Var fallback) | module globals (float/str/list/tuple/dict/call result/module alias), imports, from-imports | FIXED (origin) unless known-int binding |
| same, unresolved free names (lambda / pattern vars Module 6 declares) | WhyML-bound locals | safe (binder-scoped, not an origin) |
| `expressions.py` `val constant {csafe}` (`_class_X`) / class constant | class objects | FIXED (origin; int class attrs exempt) |
| `expressions.py` `val [function] get_{attr} (x: int) : int` | attribute of module/class/importlib/`__import__` object | FIXED (derived from origin receiver) |
| same, receiver a parameter / local / `self` field | object attributes of unknown type | RESIDUAL |
| `statements.py` `val getattr_{cls} (x: cls) (f: int) : int`, `getattr_2` | `self.attr` not a record field | FIXED for class-level non-int attrs (hash match); instance attrs RESIDUAL |
| `expressions.py` `pycsl_getattr_{unknown,missing,default}_<h>` | `getattr(o, n[, d])` | FIXED (origin; #47 default reflexivity kept) |
| `expressions.py` `val subscript_get (x: int) (i: int) : int` | element of an unmodelled container | FIXED when container tainted; param/local containers RESIDUAL |
| `stmt_control_flow.py` `val iter_get`, `hval_iter_get_other` | loop element of an unmodelled iterable | FIXED when iterable tainted; `range` known-int |
| `expressions.py` call stubs `val {arity_fn} () : int`, `(x_i: int) : int`, `{pname}`, `{name}_{n}` (~8822/9102/9116/10797/10809/11656) | imported-module / builtin calls (`time.time`, `random.random`, `os.getcwd`, `float.fromhex`, `importlib`, `__import__`, `eval`, `pow`, `dict`, `float`) | FIXED (origin unless known-int) |
| same, method calls on params / locals / `self` (`self__m_k`, `c_m_k`) | method results | FIXED when receiver tainted or the user method returns a fallback; else RESIDUAL (user `-> int` method body verified int) |
| `iter_length`, `hval_values_len`, `hval_iter_len_other`, `hval_len_other`, `typeof_op`, `int_to_string` | lengths, type tags, rendering | safe (int-only / sink) |
| `pycsl_none`, `pycsl_ellipsis`, `str_hash_op`, `str_of_int_hash`, `str_of_bool_hash`, `{cls}_hash_`, `contains_check`, `hasattr_check`, `isinstance_op`, `in_globals_op`, `in_scope_op` | model encodings (None/Ellipsis identity, string/bool hashes, booleans) | safe (their own models; not fallbacks) |
| `str_concat`, `join_1`/`join_array`, `str_of_int`, `str_of_value_op`, `{wf}_conv` (`abs_conv`, `repr_conv`), `list_comp`/`set_comp`/`dict_comp`/`list_new`, `literal_eval_op`, `unknown_op`, `py_type_name_of`, `array_slice`, `py_pow` | int-ENCODED strings / collections / unknown results of model ops | tainted when applied to a tainted argument (4262 `abs(F)`); their OWN results over untainted inputs RESIDUAL (string-as-int encodings; not this route's fallbacks; `py_pow` is route #259's) |
| `setattr_*`, `subscript_set` | unit stores | sinks |

**Probe table** (CPython ground truth in each `__main__`; base = 0da66911 full proof; after = this branch):

| witness | CPython | base | after |
|---|---|---|---|
| 4230-4235 F1 #322 bypasses (re-export, from-re-export, importlib, `__import__`, local / global module alias) | violates | PROVED | REFUSED (R325) |
| 4236 t06 `x < EPS or x >= EPS+1 or x == EPS` | violates | PROVED | REFUSED |
| 4237 r05, 4238 r12 (`F: float = 0.5`), 4239 r13 (`X = mk()` list), 4240 t03 `int(F) == F` | violate | PROVED | REFUSED |
| 4241 c01 `C.R`, 4242 c06 `self.R`, 4243 c05 enum `.value`, 4244 c07 `T[0]` | violate | PROVED | REFUSED |
| 4245 r02 `consts325.F`, 4246 q02 `consts325.S * 0 == 0` | violate | PROVED | REFUSED |
| 4247 p08 `time.time()`, 4248 q01 `random.random()`, 4249 q03 `os.getcwd()`, 4250 q07 `float.fromhex` | violate | PROVED | REFUSED |
| 4251 alias chain, 4253 param flow into `k(x: int)`, 4254 list store, 4255 if-expression, 4256 `float(s) == itself` (nan), 4257 nan trichotomy, 4258 `for v in T`, 4259 dict global, 4260 lambda case-fold, 4261 method returning class attr, 4262 `abs(F)`, 4263 `c.upper()` on `os.getcwd()` | violate | PROVED (13 new false proofs) | REFUSED |
| 4252 return flow `h() -> float` | violates | FAIL | REFUSED |
| 4264-4271 controls (int globals, int class attr, `sys.maxsize`, `randint`, opaque `==` literal, opaque passthrough, `float_info.dig`, user `-> int` method) | ok | (emission-identical) | PROVED |

**Blast radius.** Corpus root (2187 base / 2182 candidate emitted): 0 MOVED, 5 GONE, all `# pycsl-expected: FAIL` false-claim
witnesses that FAILED and now REFUSE: 1066 (`float("nan") + 1`), 2702 / 2706 (`pow(2, -1) % 1`), 3432 / 3433 (`dict(func)`
copy read as a map); `byte-diff-compare --expect-gone <5>` rc=0. pyref 2186/2186 0/0/0 rc=0. Mirror 53/53 0 MOVED / 0 GONE /
0 APPEARED (`--min-files 50` rc=0) — no mirror file loses its emission, so no OWED mirror proof. No previously-proved corpus
file fails: no latent false proof surfaced in the corpus (the 13 new false proofs are the scratch shapes 4251-4263).
**Gates** (logs in the r325 worktree, removed after the run; exit codes): witnesses at base 33/34 rc=0 PROVED (4252 rc=1) -> after 34/34 rc=1 REFUSED;
controls 4264-4271 rc=0 after. Base sweeps (0da66911 worktree) and candidate sweeps: byte-diff-compare root rc=0 with `--expect-gone`
of the 5 above, pyref rc=0 (`--min-files 2000`), mirror rc=0 (`--min-files 50`). run-soundness-planes.sh fast 61/61 rc=0; slow
check-getattr-erasure rc=0 (DECLARED 0) and check-stdlib-modules-verify rc=0, each run on its own; check-self-annotate-sync.sh rc=0
(926 verbatim); self-annotate-mirror-check.sh rc=0 (53); doc-coherency --check rc=0; check-assumed-facts rc=0 (85 facts, ledger 3
unchanged); check-trusted-raises-honesty rc=0 (ratchet 61); check-refusal-witness-coverage rc=0 (274 demonstrated, 5 = ceiling; it
was 6 > 5 at base because #322's census rows were still owed; rows for 4190-4202 were added through `_census_row`, along with 4230-4263
and the 5 movers). No gate was loosened, no axiom was added, no helper def was added.
**Residuals** (not fixed; they fail closed or are out of scope):
(1) attribute / subscript / method-call fallbacks over PARAMETERS, plain locals and INSTANCE attributes are not origins: `def f(o): o.x % 1`
and an unannotated parameter typed `int` belong to the parameter-annotation trust. Making them origins refused 13 mirror files
(measured), so it was left out.
(2) the int-encoded results of model operations (`str_concat`, `join`, `list_comp`, `repr_conv`, `py_pow`, ...) over UNTAINTED inputs are
still `int`, the same root cause one level down; `py_pow` with a negative exponent is route #259's.
(3) user-module int attributes (`consts.K` with `K = 5` in the imported module) are over-refused, because the imported source is not
read (module resolution is route #326's area).
(4) for `getattr(o, n, d)`, #47's per-default constant keeps its reflexivity, so a NaN-valued default expression would compare equal to
itself.
(5) the check is text-level over machine-generated WhyML. Its scoping is approximate in the over-refusing direction, except for pattern
and `for` binders, which are scoped to the whole declaration.
(6) `int(F)` of a float global is refused even where the claim holds in CPython (over-refusal).
