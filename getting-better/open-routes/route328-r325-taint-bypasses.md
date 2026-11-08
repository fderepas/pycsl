# OPEN ROUTE #328 — BYPASSES OF THE #325 TAINT CHECK: non-simple module bindings, tuple unpacking, emitter-generated binders
**Status: REPAIRED (gen #37, 2026-10-24; candidate, see REPAIR), was OPEN (2026-10-24), Severity 1.** Red-team round 20; driver-reproduced on main a8dec3db..1333328f (rc=0; CPython violates).
Witnesses `witnesses-r328/`: origins only collect simple top-level `Name = ..`: `A, B = 0.5, 1` (t16), `try: A = math.pi except: A = 0` (t18 — brings
back the original #322 case), `if True: A = ..` (t20), module-level `for A in [0.5]` (t17), walrus (t19), `A, *REST = [...]` (t22); inside a function
`a, b = F, 1` lowers to `let (_tu_a, _tu_b) = (f, 1)` and `_tu_a` is not tainted (t07; t11 re-opens #325's t06 via `e, _ = EPS, 0`); pattern binders
scoped to the whole declaration: `with Return r -> r` hides a global `R` (n36, n38: t06 trichotomy via `R = RATE`), `| Some v_ ->` hides a global `V_` (n33).
Repair: origins = every module/class-level binding form (all targets of Assign/AugAssign/AnnAssign/For/With/Try/Match/walrus/starred, at any
nesting); propagate taint through tuple/starred unpacking; scope binders precisely (or avoid generated binder names that can collide with
user names — coordinate with #327's injective mangling).

## REPAIR (2026-10-24, r328 executor off aa1cf01c; witnesses 4330-4340)
**Design.** All three routes extend #325's inline check over the EMITTED WhyML in `_run_pipeline` (`src/pycsl/pycsl.py`,
mirror twin `\trusted`; no new def, no helper extraction, no axiom: ledger 3), in commit 0edf93ea (code) + corpus/census/docs commit.
- ORIGINS = every module / class-level binding form at ANY nesting outside a function / lambda body: Assign / AnnAssign /
  AugAssign targets incl. tuple and starred elements, `for`, `with`, `except .. as`, walrus, `match` captures, nested `def` /
  `class` (an AST worklist replaces the top-level `Name = ..` scan). A target paired with a value (`A = e`, `A, B = e1, e2`) is
  classified by that value; `for x in range(..)` binds an int; any other target is of unknown type. So `A, B = 1, 2`,
  `if c: K = 3`, `for I in range(3)` stay KNOWN-INT (controls 4354, 4355).
- FLOW: a tuple pattern `let (_tu_a, _tu_b) = (u, v) in` taints exactly the component u sits in (all names when the right-hand
  side is a whole tainted term); names inside a `let (..) =` pattern are binders, not uses (control 4356).
- BINDERS: a `match` / `try` arm's pattern variables scope from the arm's `|` / `with` to the next arm (or the block's `end`),
  a `for` index over its `do .. done` (both were declaration-wide, so `with Return r -> r` hid a global `R`, `| Some v_ -> v_`
  a global `V_`). Robust to #327's identifier work: the scope is positional, not name-keyed (control 4360: int `R` proves).
- Two sinks were needed to keep the mirror emitting (measured: 7 mirror files GONE without them): the KEY of `Map.get` /
  `Map.mem` / `Map.set` (equality-only, the result is the map's value) and a `writes` / `reads` / `alias` item (a location);
  and a `Return_<ty>` constructor is the return wrapper (W3), like `Return`.

**Probe table** (base = aa1cf01c: driver-reproduced full proof rc=0 + `--no-proof` emit rc=0 here; after = this branch):

| witness | CPython | base | after |
|---|---|---|---|
| 4330 t16 `A, B = 0.5, 1` | violates | PROVED | REFUSED (R325) |
| 4331 t18 `try: A = math.pi` | violates | PROVED | REFUSED |
| 4332 t20 `if True: A = 0.5` | violates | PROVED | REFUSED |
| 4333 t17 module `for A in [0.5]` | violates | PROVED | REFUSED |
| 4334 t19 walrus `(A := 0.5)` | violates | PROVED | REFUSED |
| 4335 t22 `A, *REST = [0.5, 1]` | violates | PROVED | REFUSED |
| 4336 t07 `a, b = F, 1` (`_tu_a`) | violates | PROVED | REFUSED |
| 4337 t11 `e, _ = EPS, 0` trichotomy | violates | PROVED | REFUSED |
| 4338 n36 `R` hidden by `with Return r` | violates | PROVED | REFUSED |
| 4339 n38 `R = RATE` trichotomy | violates | PROVED | REFUSED |
| 4340 n33 `V_` hidden by `Some v_` | violates | PROVED | REFUSED |
| 4354 / 4355 / 4356 / 4360 controls | ok | (emission-identical) | PROVED (see gates) |

**Blast radius** (shared by #328 / #330 / #331; sweeps of aa1cf01c (base worktree) vs this branch, compared once per tree):
corpus root 2191 base / 2194 candidate: **0 MOVED, 8 GONE**, every one `# pycsl-expected: FAIL` and FAIL -> REFUSED (R325):
1480, 1483, 1484, 1485 (route #148/#149 non-integral float fields, `c.r > 2`), 1851 (generic `T` field), 2112 / 2113
(`Optional[str]` / `Optional[list]` dataclass fields), 2392 (`Any` field); `byte-diff-compare --expect-gone <8>` rc=0 (11 new
sources ignored). pyref 2186/2186 0/0/0 rc=0 (`--min-files 2000`). Mirror 53/53 0 MOVED / 0 GONE / 0 APPEARED
(`--min-files 50`) rc=0 — **no OWED mirror proof** (a first candidate lost 7 mirror files — `writes {self.f}` items, a
`Map.get` key, a `Return_<ty>` wrapper, a `join_1` origin — each fixed by the sink rules above, not by a narrower origin).
Measured and narrowed: bare-container elements as origins = 90 GONE (declared instead); integral float field
literals = 2 (1490, 2132 PASS controls; carried); None / Optional `=` = 3 (1675, 1678, 2111; `=` admitted).
No previously-proved corpus file fails: no latent false proof surfaced; the new false proofs are the red-team shapes.
**Gates** (logs `.r328tmp/g/`, removed at the end; rc): witnesses 4330-4353 REFUSED (census `_census_row` rows, full pycsl
run; `--no-proof` screen identical), base `--no-proof` emits all 24 rc=0 (driver full-proof repro rc=0 at main); controls
4354-4362 and 4363-4364 full proof rc=0 (heavy.sh); run-soundness-planes.sh fast 61/61 rc=0 (first run 59/61: the new
4363/4364 self-check and a raise-on-[] in 4363, fixed in 657bd460); check-getattr-erasure rc=0 (DECLARED 0); check-stdlib-modules-verify
rc=0 (each run on its own); check-self-annotate-sync.sh rc=0 (926 verbatim); self-annotate-mirror-check.sh rc=0 (53); doc-coherency --check rc=0;
check-assumed-facts rc=0 (85 facts, ledger 3 unchanged); check-trusted-raises-honesty rc=0 (ratchet 61);
check-refusal-witness-coverage rc=0 (274 demonstrated, 5 = ceiling; rows for 4330-4353 and the 8 movers added through
`_census_row`, main-tree paths); check-dropped-mutation rc=0 (0 / 51 / 5 / 0); check-corpus-executes rc=0;
check-corpus-contract-truth-args rc=0. No gate loosened, no axiom, no helper def.
**Residuals**: (1) a field initialised from an UNANNOTATED parameter or an unshown expression stays int (#325 residual 1);
(2) an integral float field literal is carried as an int (routes #148/#236), so float rounding laws at magnitude >= 2**53 and
`str()` of it are not modelled; (3) bare-container elements: BARE-CONTAINER-INT (declared, strict flag); (4) a container
FIELD's elements (`self.xs = []` then `xs[0]`) and dict values of unknown type are not origins; (5) the check stays
text-level over generated WhyML (#325 residual 5), now with arm / loop-precise binders; (6) a str field is a strict
origin, so `c.s == c.s` is over-refused.
