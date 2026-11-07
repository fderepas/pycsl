# OPEN ROUTE #338 — OVERRIDE RETURN TYPES NOT COMPARED (`-> int` overridden `-> float`), and FIELD STORES FROM OUTSIDE THE CLASS HIERARCHY NOT COUNTED BY #334
**Status: REPAIRED, candidate (gen #37, 2026-10-24; r338 executor off d175a70d — see REPAIR). Was OPEN, Severity 2.** Red-team round 23; driver-reproduced on main (combined files rc=0; CPython violates).
Witnesses `witnesses-r338/`: F4_residuals.py (3): #334 residuals 6 and 1 (overridden `-> int` method returning float used as initialiser;
unannotated-param initialiser) + new g_call_override: base `-> int` overridden `-> float` called as `b.m()` on a base-typed parameter — the refinement
goal is `true -> true`, return types never compared (mypy rejects, CPython runs). F5_external_store.py (2): a float stored into an unannotated
int-inferred field from `__main__`/module code (`c.r = 0.5`, setattr) is not among #334's stores (class/bases/descendants only).
Repair: the #277 override refinement must compare return (and parameter) types — refuse an override whose return annotation is not a subtype;
#334's store census must include stores from module-level code and any function (or refuse external field stores of non-int values).

## REPAIR (2026-10-24, r338 executor off d175a70d; code e8c3d3e5 / 5d96d6e1 / ef4c3d57, corpus f8c6d9aa / 355942e6, census 88901d08, docs 2e529ccc + route docs)
**Design.** Inline in `_run_pipeline` (mirror twin `\trusted`; no new def, no lambda, no helper extraction, no axiom: ledger 3).
- (a) **R5 in the route #278 block** (annotations §7.24, translational §T.6.35, static semantics R5). For every recorded override pair
  the two Python defs are read from the SOURCE AST (the IR flattens `Optional[int]` to `_union_*`, `List[int]` to `list`). The
  override's return annotation must be a SUBTYPE of the base's, each base positional parameter annotation a subtype of the
  override's at the same position. Per member of `Union` / `Optional` / `|`: same type (`typing.` / `List`-`list` normalised),
  `bool` <: `int`, a file class <: its ancestors, anything <: `Any` / `object`; `int` is NOT <: `float` (model `int` / `real`); absent =
  `Any` (no constraint on the wider side, refused on the narrower: an unannotated override of `-> int`). Refusal
  `PYCSL-SEM-OVERRIDE-REFINEMENT` (advice extended; re-audited, hash updated). `--assume-class-exact` turns it off with R1-R4.
- (b) **External store census** (#334 block). A whole-module walk (enclosing def tracked) collects every attribute store not
  already counted as a `self` store (id set): `=` / annotated / `+=` (plus an unknown dict-value store) / `for` / `with` /
  comprehension / tuple-paired targets, `del x.f`, `setattr` / `delattr` / `object.__setattr__|__delattr__` (deletion = a non-int
  marker; dynamic name = `*`), `x.f[k] = e`, `x.f.update|setdefault|__setitem__`, `__dict__` / `vars(x)` stores (`*`). The
  store joins: the receiver's class (a method's `self`, a parameter annotated `K`, a local every binding of which is `K(..)`);
  NO class for a parameter annotated with builtin scalar/container names only (annotation trust); otherwise EVERY file class
  storing a field of that name. The #334 kind walk then classifies them as usual (a value of unknown type is still carried under a
  field declared `int`).
- (c) **#334 residual 1**: an UNANNOTATED parameter initialiser is UNK when UNVERIFIED code of the module (module level,
  `__main__`, class bodies, decorators, defaults; class BASES excluded) names the storing def, its class or a descendant;
  otherwise INT (verified callers are WhyML-typed). The blunt "always UNK" was measured first: root/pyref inert but the mirror
  `frontend/Module1_Ingestor.py` GONE (`_Target(.., report_line, ..)`), hence the refinement.
- (d) **#334 residual 6** closed by R5 (`self.r = self.m()` with `m` overridden `-> float` is refused); and `k.m()` on a receiver
  typed / constructed as a file class `K` is INT when `m` is `-> int` in `K` or a base (R5 keeps it so) — needed by root 3901
  (`k.n += k.bump()`, GONE without it, measured).

**Probe table** (full pycsl proof, rc; base = d175a70d worktree; CPython ground truth = each `__main__`):

| shape | corpus | CPython | base | after |
|---|---|---|---|---|
| F4 g_call_override `B.m -> int`, `S.m -> float`, `b.m() % 1 == 0` | 4530 | violates | PROVED (0) | REFUSED (1, R5) |
| F4 g_init_override (#334 res. 6) `self.r = self.m()` | 4531 | violates | PROVED (0) | REFUSED (1, R5) |
| F4 g_unannot_init (#334 res. 1) `U(0.5)` in `__main__` | 4532 | violates | PROVED (0) | REFUSED (1, R325) |
| unannotated override of `-> int` returning 0.5 | 4533 | violates | FAILED (1) | REFUSED (1, R5) |
| parameter narrowed `x: int` -> `x: bool` | 4534 | violates | FAILED (1) | REFUSED (1, R5) |
| F5 g_main_store `c.r = 0.5` in `__main__` | 4535 | violates | PROVED (0) | REFUSED (1, R325) |
| F5 g_main_setattr `setattr(d, "r", 0.25)` | 4536 | violates | PROVED (0) | REFUSED (1) |
| module-level `K.r = 0.5` | 4537 | violates | PROVED (0) | REFUSED (1) |
| `c.r += 0.5` in `__main__` | 4538 | violates | PROVED (0) | REFUSED (1) |
| `del c.r` in `__main__` | 4539 | AttributeError | PROVED (0) | REFUSED (1) |
| `delattr(c, "r")` in `__main__` | 4540 | AttributeError | PROVED (0) | REFUSED (1) |
| controls: external int stores 4541, `-> bool` under `-> int` 4542, covariant returns / contravariant param 4543, unannotated param with verified callers only 4544 | — | ok | PROVED | PROVED |
| combined F4_residuals.py / F5_external_store.py | — | violates | PROVED (0) | REFUSED (1) |

Scratch, not filed: a function / other-class method storing `c.r = 0.5` (`spoil(c: C)`) and `c.d["a"] = 0.5` in `__main__` already
FAIL at base (Why3 `real` vs `int` type error; module-scope computed-receiver refusal) and are REFUSED after.

**Blast radius** (base sweeps in a d175a70d worktree, candidate sweeps of the final code, compared once per tree): root 2228 base /
2232 candidate **0 MOVED / 0 GONE / 0 APPEARED** (4 new sources = controls) rc=0; pyref 2186/2186 0/0/0 rc=0 (`--min-files 2000`);
mirror 53/53 **0/0/0** (`--min-files 50`) rc=0 — **no OWED mirror proof**. Pre-measurement by AST scan: no override pair in the corpus,
pyref, mirror or stdlib changes a return / parameter annotation. **No latent false proof** (nothing previously proved moved); the 9 new
false proofs are the red-team / scratch shapes 4530-4532, 4535-4540.

**Gates** (logs `.r338tmp/g/`, removed at the end; rc): witnesses table above; controls rc=0; byte-diff-compare root rc=0, pyref
rc=0, mirror rc=0; check-self-annotate-sync.sh rc=0 (926 verbatim); self-annotate-mirror-check.sh rc=0 (53); run-soundness-planes.sh
fast **61/61** rc=0 (first run 59/61: check-vacuous-drivers flagged the first 4543 `return 1` control — rewritten to rest on `B.p`'s
contract — and check-refusal-advice-audited flagged the edited #278 advice — re-audited, hash `dd0cf228cde7`); check-getattr-erasure
rc=0; doc-coherency --check rc=0; check-assumed-facts rc=0 (85 facts, ledger 3); check-trusted-raises-honesty rc=0 (ratchet 61);
check-refusal-witness-coverage rc=0 (281 / 5, ceiling 5; rows 4530-4540 via `_census_row`, main-tree paths); check-dropped-mutation
rc=0 (0 / 51 / 5 / 0). `--slow` planes not run. No gate loosened, no axiom, no helper def.

**Residuals.** (1) The census is PER FILE: an unverified IMPORTER that constructs `U(0.5)` or stores `c.r = 0.5` is not seen (as for
every modular claim). (2) Only int-typed labels are origins: deleting / externally storing a str or list field is not checked here.
(3) Annotation trust: a receiver parameter annotated with builtin types only is assumed to hold no file-class instance. (4) R5 reads
both defs from THIS file: an override of a base defined in an imported module is not compared (route #277's p260 shape); keyword-only
/ `*args` parameters and `@staticmethod` positions are not compared. (5) `int` under `float` is refused (stricter than PEP 484; 0
movers). (6) Stores not spelled as attributes (`exec`, `operator.setitem(vars(c), ..)`, `copy` / `pickle`) are not counted. (7)
Observed, not this route's: a call `b.p(n)` on a FIELDLESS base class lowers to an unconstrained stub (fail-closed; #337's area).
