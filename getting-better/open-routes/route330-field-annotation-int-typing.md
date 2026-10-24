# OPEN ROUTE #330 — INSTANCE FIELDS, MODEL-OP RESULTS AND BARE/COMPLEX ANNOTATIONS TYPED `int` (int laws proved of floats/strs/complex)
**Status: REPAIRED (gen #37, 2026-10-24; candidate, see REPAIR), was OPEN (2026-10-24), Severity 1.** Red-team round 20; driver-reproduced on main a8dec3db..1333328f (rc=0; CPython violates).
Witnesses `witnesses-r330/`: `self.r = 2.5` then `int(c.r) == c.r` proves (i07; field `{ r = (any int) }`), `c.r % 1 == 0` (a07), `self.r` in a method (i03),
via a parameter `c: C` (i04), `self.s = "ab"` emitted `{ s = 0 }` then `c.s * 0 == 0` (i11); model-op results int-encoded: `repr(n) * 0 == 0` (r02),
`f"{n}" * 0 == 0` (r07); bare `xs: List` / `xs: list` give int elements (d08, e11b; #249 residual); `z: complex` typed int so `z*z != -1` proves
(CPython False for 1j) (e10; #43 only refuses complex LITERALS).
Repair: extend #325's taint to instance fields whose initialiser/annotation is not int, to model-op results that encode non-int values, to
bare/unknown element annotations, and refuse (or type correctly) a `complex` annotation.

## REPAIR (2026-10-24, r328 executor off aa1cf01c; witnesses 4341-4350, assumption 4363-4364)
**Design.** All three routes extend #325's inline check over the EMITTED WhyML in `_run_pipeline` (`src/pycsl/pycsl.py`,
mirror twin `\trusted`; no new def, no helper extraction, no axiom: ledger 3), in commit 0edf93ea (code) + corpus/census/docs commit.
- (a) FIELDS: a record label typed `int` (parsed from the emitted `type` declarations; label = `transpiler._field_label(record,
  f)`, inherited through the class bases) of a field with a SHOWN non-int class-level / `self.f = ..` initialiser or annotation
  (float / str / bytes / None literal, f-string, display, `/`, `float/str/repr/..(..)`, an imported value, a non-int global, a
  parameter annotated non-int, an annotation other than `int` / `bool`) is an origin; the unit is the read `<recv>.<label>`.
  Targeted, as #325 measured (all attributes of params/locals refused 13 mirror files): an unannotated-parameter initialiser
  stays int. An INTEGRAL float literal (`2.0`, |v| < 2**53) stays carried as that int (routes #148 / #236: 1490, 2132 keep
  proving). The generated frame `X.f = old X.f` and `writes { X.f }` items are admitted (control 4357).
- (b) STRING-ENCODING model ops are origins: `repr_conv`, `format_conv`, every other `*_conv` except `abs/bool/int/round/len/ord/
  hash`, `str_of_int_hash`, `str_of_bool_hash`, `str_of_value_op`, the int `str_concat` joiner. A string equals itself, so their
  `=` / `<>` stay admitted everywhere (control 4358 `f"{n}" == f"{n}"` proves).
- (c) BARE containers: making every bare-container element an origin refused **90 corpus files** (measured; 76 unlabelled proved
  drivers, 13 FAIL, 1 PASS) — disproportionate, so it is a DECLARED MODEL ASSUMPTION **BARE-CONTAINER-INT** (soundness-report
  entry, README, static-semantics + translational §T.10.5, check-assumed-facts docstring) with the opt-in
  `--strict-bare-containers` that turns the element reads `p[i]` / `(subscript_get p i)` into origins (4348 / 4349 REFUSED;
  default-mode counterexamples 4363 / 4364 PROVE, like LATIN1-STR's 3020).
- (d) a `complex` annotation anywhere (param, return, AnnAssign) is refused outright (0 corpus / mirror uses).

**Probe table** (base = aa1cf01c, as for #328):

| witness | CPython | base | after |
|---|---|---|---|
| 4341 i07 `int(c.r) == c.r`, `self.r = 2.5` | violates | PROVED | REFUSED (R325) |
| 4342 a07 `c.r % 1 == 0` | violates | PROVED | REFUSED |
| 4343 i03 `self.r` in a method | violates | PROVED | REFUSED |
| 4344 i04 via parameter `c: C` | violates | PROVED | REFUSED |
| 4345 i11 `self.s = "ab"`, `c.s * 0 == 0` | violates | PROVED | REFUSED |
| 4346 r02 `repr(n) * 0 == 0` | violates | PROVED | REFUSED |
| 4347 r07 `f"{n}" * 0 == 0` | violates | PROVED | REFUSED |
| 4348 d08 `xs: List`, `--strict-bare-containers` | violates | PROVED | REFUSED |
| 4349 e11b `xs: list`, `--strict-bare-containers` | violates | PROVED | REFUSED |
| 4363 / 4364 same, default mode (BARE-CONTAINER-INT) | violates | PROVED | PROVED (declared assumption) |
| 4350 e10 `z: complex` | violates | PROVED | REFUSED |
| 4357 / 4358 / 4359 / 4361 controls | ok | (emission-identical) | PROVED (see gates) |

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
