# OPEN ROUTE #334 — #330/#331 FIELD-ORIGIN GAPS: non-int field initialisers through locals/walrus/negative pow, tuple-target __init__, integral floats, unknown dict values
**Status: REPAIRED, candidate (gen #37, 2026-10-24; r334b executor off 1b425056 — see REPAIR). Was OPEN, Severity 1.** Red-team round 21; driver-reproduced on main ec549509 (rc=0; CPython violates).
Witnesses `witnesses-r334/`: the field-initialiser classifier only recognises literal / `/` / some calls / non-int-annotated params / globals; these lower to
`{ r = (any int) }` without tainting the label: `x = 2.5; self.r = x` (f02), walrus (f20), `2 ** -1` (f06), `10 ** -1` with `c.r * 10 == 1` False (f22; the
#259 py_pow obligation is also lost), str via a local (f18), None via a local under no_exception (f24), str via local `c.s - c.s` (f25);
tuple-target `self.r, self.s = 2.5, 1` escapes #315 (class opaque, `get_r`) and `c.r % 1 == 0` proves (o03); integral float `self.r = 3.0` carried as int:
`c.r*10**17 + 1 != c.r*10**17` proves (p01), `len("ab" * c.r)` with r=2.0 under no_exception (CPython TypeError) (p10); dict values of unknown
type: field `{"a": 0.5}` then `c.d["a"] % 1 == 0` (k04), bare `d: dict` param `map string (option int)` proves the same even with
--strict-bare-containers (k01; BARE-CONTAINER-INT lists only list/List/Sequence/tuple).
Repair: classify a field origin by the TYPE of the initialiser expression (type inference over locals/walrus/pow/calls), not by syntactic shape —
any initialiser not provably int taints the label; integral float literals are floats (taint, or keep int only where #148/#236 controls need it
and prove those uses are float-safe); dict values of unknown/bare type are origins (extend BARE-CONTAINER-INT docs or taint); tuple-target
field initialisation must be either modelled like single targets or refused by #315.

## REPAIR (2026-10-24, r334b finishing executor off 1b425056; commits 43740172 (r334 draft, committed as found), 24b9295f, 7e75582d, 9bbf1701 (code), 7e75582d (corpus), 41ac87f2 (census), 054a4330 (docs) + route docs)
**Design.** Still inline in #325's `_run_pipeline` block (mirror twin `\trusted`; no new def, no helper extraction, no axiom:
ledger 3). The #330 SHAPE whitelist is replaced by a TYPE classifier over the Python AST (annotations §7.21, translational §T.6.32):
- STORES of field `f` of class `C` = every store in `C`, its bases AND its descendants (driver witness i01: a receiver typed `B` may
  hold an `S(B)`): class-level / `self.f = ..` / `self.f: T = ..`, tuple targets paired element-wise (o03), starred / `for` / `with` /
  comprehension targets (unknown value), `+=` as `0 op e`, `setattr(self, "f", e)` (a dynamic name taints every field), dataclass
  `field(default=..)`; dict mode: display values, `self.d[k] = e`, `.setdefault`, `.update` / `|=` (unknown).
- KINDS per stored value: INT (int / bool literal; `+ - * // % << >> & | ^` over INT; `**` by a non-negative int literal; a local of
  the storing def through EVERY binding; walrus; int / unannotated parameter; known-int global; another field through its stores;
  `len int ord hash id bool round(x)`; `abs min max` of INT; a user `-> int|bool` function / method), NONE (#331), IFLOAT (integral
  float literal, |v| < 2**53), OTHER (shown non-int: float / str literal, `/`, `2 ** -1`, displays, f-strings, `float(..)`, module
  values, non-int-annotated sources), UNK (unknown type: attribute of an untyped object, unknown call).
- The `int` label is an origin unless every kind is INT. UNK is dropped when a store DECLARES the field `int` / `bool` /
  `Final[int]` / `ClassVar[int]` (annotation trust, as for an `int` parameter) — required by the mirror: `pure_ast` `self.type: int =
  t.type`, `statements` `_slice_set_tmp_counter: int = 0` + `getattr(self, .., 0) + 1` (both GONE without it, measured).
- IFLOAT: admitted only as a DIRECT comparison operand (`< <= > >= = <>`; CPython compares int / float exactly): 1490 `c.r > 1`
  keeps proving; arithmetic / argument uses (p01, p10, and 2132's `p.k + p.m`) are refused.
- DICT VALUES: a dict field whose values are not all INT is a VALUE origin (`match Map.get u k with | Some v` reads; `| Some _` and
  `Map.mem` only test membership). A bare `dict` / `Dict` / `Mapping` PARAMETER joins the declared BARE-CONTAINER-INT assumption
  (soundness report, strict-flag help, README, static-semantics, translational §T.10.5, check-assumed-facts docstring);
  `--strict-bare-containers` makes its values origins (k01 = 4427). Default-origin was measured: 3 corpus (0199, 0621, 0624) + 1
  MIRROR (core_ir_semantic) GONE, so it is declared, not default.
- OPAQUE classes (no record type; `C()` a stub, `c.f` a getter): the constructor stub is an origin, getters of provably-int fields
  stay int (o03's `get_r` refused, control 4445 `get_s` proves).
- One new SINK (mirror ConcurrencyChecker GONE without it): an argument at a `'a`-typed parameter of a `val` (`str_mod_op "fmt" (a,
  u)`: no int theory applies there); the head is found skipping string-literal arguments, in a separate scan so the #325 head
  scan is unchanged (a global string skip moved `statements` — measured, reverted).

**Probe table** (CPython ground truth in each `__main__`; full pycsl proof; base = 1b425056 worktree, after = this branch):

| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| f02 `x = 2.5; self.r = x`, `int(c.r) == c.r` | 4420 | violates | PROVED | REFUSED (R325) |
| f06 `self.r = 2 ** -1` | 4421 | violates | PROVED | REFUSED |
| f18 str via local, `c.s * 0 == 0` | 4422 | violates | PROVED | REFUSED |
| f20 walrus `(y := 2.5)` | 4423 | violates | PROVED | REFUSED |
| f22 `10 ** -1`, `c.r * 10 == 1` decided False | 4424 | violates | PROVED | REFUSED |
| f24 None via local, `no_exception` `c.r * 0` | 4425 | TypeError | PROVED | REFUSED |
| f25 str via local, `no_exception` `c.s - c.s` | 4426 | TypeError | PROVED | REFUSED |
| k01 bare `d: dict`, `--strict-bare-containers` | 4427 | violates | PROVED | REFUSED |
| k04 dict field `{"a": 0.5}` | 4428 | violates | PROVED | REFUSED |
| o03 `self.r, self.s = 2.5, 1` (opaque class) | 4429 | violates | PROVED | REFUSED |
| p01 `self.r = 3.0`, `c.r*10**17 + 1 != c.r*10**17` | 4430 | violates | PROVED | REFUSED |
| p10 `self.r = 2.0`, `no_exception` `len("ab" * c.r)` | 4431 | TypeError | PROVED | REFUSED |
| q08 field from float field `self.r = self.s` | 4432 | violates | PROVED | REFUSED |
| q16 `for self.r in [2.5]` | 4433 | violates | PROVED | REFUSED |
| q29 `self.r, *self.t = 2.5, 1` | 4434 | violates | PROVED | REFUSED |
| s06 dict field via local | 4435 | violates | PROVED | REFUSED |
| s07 `self.d = dict(a=0.5)` | 4436 | violates | PROVED | REFUSED |
| q02 `x = 2.5; self.r: int = x` (declared, shown float) | 4437 | violates | PROVED | REFUSED |
| q12 `self.r = abs(-2.5)` | 4438 | violates | PROVED | REFUSED |
| i01 (driver) subclass `self.r = 0.5`, `g(b: B)` | 4439 | violates | PROVED | REFUSED |
| k01 default mode (BARE-CONTAINER-INT counterexample) | 4443 | violates | PROVED | PROVED (declared) |
| controls: provably-int inits 4440, integral-float compare 4441, int dict field 4442, dataclass `p.m == 2` 4444, opaque-class int component 4445; 1490 | — | ok | — | PROVED |
| 2132 `p.k + p.m == 7` (`m: int = 2.0`; a TRUE claim) | 2132 | ok | PROVED | REFUSED (declared over-refusal; marked FAIL) |

Scratch probes, not filed (all FAIL or REFUSED after): `str(c.r) == "3"`, `f"{c.r}"`, `repr(c.r)`, `isinstance(c.r, int)`,
`type(c.r) == int` over `self.r = 3.0`, and list field `self.xs = [0.5]` then `c.xs[0] % 1 == 0` — all emit and FAIL in Why3
(not proved); `self.r += 0.5`, `self.r = 0; self.r = self.r * 2.5`, `1 if b else 2.5`, a method rebinding `self.r = 0.5` — REFUSED.

**Blast radius** (base sweeps in a 1b425056 worktree, candidate sweeps of the final code, compared once per tree): root 2223 base /
2228 candidate: **0 MOVED, 1 GONE (2132, declared; `--expect-gone`), 0 APPEARED**, 6 new sources ignored; rc=0. pyref 2186/2186
0/0/0 rc=0 (`--min-files 2000`). Mirror 53/53 **0 MOVED / 0 GONE / 0 APPEARED** (`--min-files 50`) rc=0 — **no OWED mirror proof**
(the draft as found lost 3 mirror files: pure_ast, statements, ConcurrencyChecker — fixed by the declared-int trust and the `'a`
sink above, not by narrowing an origin). No previously-proved corpus file fails: **no latent false proof** in the corpus; the 20 new
false proofs are the red-team / scratch shapes 4420-4439.

**Gates** (logs `.r334btmp/g/`, removed at the end; rc): witnesses 4420-4439 base full proof 20/20 PROVED rc=0 -> after 20/20 REFUSED
rc=1; controls 4440-4445 + 1490 full proof rc=0; byte-diff-compare root rc=0 (`--expect-gone 2132`), pyref rc=0, mirror rc=0;
check-self-annotate-sync.sh rc=0 (926 verbatim); self-annotate-mirror-check.sh rc=0 (53); run-soundness-planes.sh fast 61/61 rc=0;
check-getattr-erasure rc=0 (DECLARED 0); check-stdlib-modules-verify: see README entry; doc-coherency --check rc=0;
check-assumed-facts rc=0 (85 facts, ledger 3 unchanged); check-trusted-raises-honesty rc=0 (ratchet 61);
check-refusal-witness-coverage rc=0 (281 demonstrated / 5, ceiling 5; rows 4420-4439 + 2132 via `_census_row`, main-tree paths);
check-dropped-mutation rc=0 (0 / 51 / 5 / 0); check-corpus-executes rc=0; check-corpus-contract-truth rc=0;
check-corpus-contract-truth-args rc=0. No gate loosened, no axiom, no helper def.

**Residuals.** (1) ANNOTATION TRUST: a field declared `int` carries values of UNKNOWN type (`self.n: int = t.n` with `t.n == 2.5`
proves `c.n % 1 == 0`), as an `int` parameter does; an unannotated-parameter initialiser stays int (#325 residual 1; the record
literal is typed at the call site). (2) An integral float is int-modelled as a comparison operand only; `c.r + 0 == 3` and 2132 are
over-refused. (3) BARE-CONTAINER-INT now also covers bare dict values (declared; strict flag). (4) A LIST / set field's ELEMENTS
are still not origins (`self.xs = [0.5]`: the probe FAILS in Why3, it does not prove — unmeasured in general). (5) A tuple-target
store in a RECORD class (`self.a, self.b = 1, 2`) emits an unbound label and fails Why3 type-checking at base and after
(fail-closed emitter gap, not this route's). (6) A method annotated `-> int` that a subclass overrides with `-> float` is still
trusted for `self.m()` initialisers. (7) Text-level check over generated WhyML (#325 residual 5).
