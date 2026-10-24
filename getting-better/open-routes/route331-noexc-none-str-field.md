# OPEN ROUTE #331 — `no_exception \all` OVER ARITHMETIC ON A None / str INSTANCE FIELD (CPython TypeError, pycsl proves no exception)
**Status: REPAIRED (gen #37, 2026-10-24; candidate, see REPAIR), was OPEN (2026-10-24), Severity 1.** Red-team round 20; driver-reproduced on main a8dec3db..1333328f (rc=0; CPython violates).
Witnesses `witnesses-r331/`: `self.r = None` then `c.r * 0` — record `{ r = pycsl_none }` with plain int arithmetic (o09); Optional field `c.r + 1 > c.r`
(o12); str field `c.s - c.s` (o10). Route #230's None guard covers locals and container reads, not fields.
Repair: arithmetic on a field whose declared/initialised type is Optional/None/str (or not provably int) must carry the #230 None/type
obligation under no_exception, or be refused; coordinate with #330's field typing.

## REPAIR (2026-10-24, r328 executor off aa1cf01c; witnesses 4351-4353)
**Design.** All three routes extend #325's inline check over the EMITTED WhyML in `_run_pipeline` (`src/pycsl/pycsl.py`,
mirror twin `\trusted`; no new def, no helper extraction, no axiom: ledger 3), in commit 0edf93ea (code) + corpus/census/docs commit.
- A `None` / `Optional[int]` / `Union[int, None]` / `int | None` field, or one initialised `None`, is a #330 field origin of
  the "None / Optional" kind: int arithmetic and orderings over it are REFUSED (CPython raises `TypeError` on the None arm,
  so a `no_exception \all` proof of `c.r * 0` was false); `==` / `!=` stay admitted (its int arm is an int, its None the
  opaque `pycsl_none`; control 4362 `c.r == None and c.r == c.r` proves; 1675 / 1678 / 2111 keep emitting). A str field
  (`{ s = 0 }`) is a strict #330 field origin. Refusal was preferred over adding the #230 obligation to field reads: the
  None arm is not distinguishable from an int in the field's `int` sort.

**Probe table** (base = aa1cf01c):

| witness | CPython | base | after |
|---|---|---|---|
| 4351 o09 `no_exception`, `self.r = None`, `c.r * 0` | TypeError | PROVED | REFUSED (R325) |
| 4352 o12 `Optional[int]` field, `c.r + 1 > c.r` | TypeError | PROVED | REFUSED |
| 4353 o10 str field, `c.s - c.s` | TypeError | PROVED | REFUSED |
| 4362 control (Optional `==`) | ok | (emission-identical) | PROVED |

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
