# wall-plan v2 — Phase 0 verdict: concrete-map / interned-key encoding spike

**Executes Phase 0 of `generic-dict-str-any-2-plan.md` §5** — the go/no-go encoding
spike for the "computation, not axiomatization" approach (design rules R-A/R-B/R-C).
A DECISION phase: GO/NO-GO with reproducible evidence, NO `src/pycsl`/mirror edits
(one hand-written `.mlw` fixture + this verdict only).

Branch `ghost-assign-bc6`. Provers: system **Alt-Ergo 2.6.2** + **Z3 4.13.3** under
**Why3 1.8.2**, 10 s timelimit. **CVC5 is not installed** on this host (`why3 config
list-provers` shows only Alt-Ergo + Z3), so best-of-N = best-of-2; the benchmark
criterion "Valid on Alt-Ergo AND Z3" is met on both provers independently below.

`\trusted` count **1248** (unchanged; asserted §6). Fixture (`git add -f`, `.mlw`
is gitignored): `test-suite/corpus/conformance/spikes/v2_pydict_spike.mlw`.

---

## OVERALL PHASE-0 VERDICT — **GO.**

| gate | required | result |
|---|---|---|
| **G1** bare-miss lookup | Valid on Alt-Ergo AND Z3 | **Valid on both** (bare); also closed by `compute_in_goal` solver-independently |
| **G2** pair-nested termination | Valid on Alt-Ergo AND Z3 | **Valid on both** (bare, direct `variant { size v }`); fuel form also Valid on both |
| **no new axiom** | 0 axiom declarations, no abstract theory | `grep -c '^[[:space:]]*axiom'` = **0**; pure inductive + `list` stdlib only (no `fmap`/`Fset`) |
| **false twins unproven** | all 4 stay unproven on both provers | **all 4 Timeout** on both provers, bare AND under compute+split |
| **compute-cost guardrail** | no blowup on largest node | large 11-key nested node closed by `compute_in_goal` in **0.02 s wall / 21 MB**; Valid bare AE 0.40 s / Z3 0.19 s |

**Both frozen benchmark goals move from fmap's Timeout/Timeout to Valid on both
provers, with no new axiom, and the model still refuses all four false twins. The
plan proceeds to Phase 1.**

The single decisive finding: **the fmap NO-GO was not a wall about heterogeneous
dictionaries — it was two fixable modelling mistakes.** (i) The bare-miss timed out
because string-keyed dispatch dragged in string theory under a recursive unfold;
interning keys as a datatype enum (R-B) turns key (dis)equality into constructor
reasoning, and `compute_in_goal` (R-A) closes the concrete miss by evaluation before
any solver runs. (ii) The pair-nested `variant` VC timed out because the size measure
`size_list (Cons h t) = size h + size_list t` makes the head-recursion obligation
`size h < size h + size_list t` require `size_list t > 0` — **false for a singleton
list**, i.e. a genuine non-decrease, not a solver weakness. Counting each cons cell
(`+ 1` per list/dict node) makes every decrease VC trivial LIA, closed on both provers.

---

## 1. The frozen-benchmark table (fmap-was-Timeout → v2-result)

Fixture: `test-suite/corpus/conformance/spikes/v2_pydict_spike.mlw`.
Exact command (whole-file; per-goal results shown):

```
why3 prove -P 'Alt-Ergo,2.6.2' -t 10 test-suite/corpus/conformance/spikes/v2_pydict_spike.mlw
why3 prove -P 'Z3,4.13.3'      -t 10 test-suite/corpus/conformance/spikes/v2_pydict_spike.mlw
```

| goal | fmap (phase0) AE / Z3 | v2 BARE Alt-Ergo 2.6.2 | v2 BARE Z3 4.13.3 | v2 with `-a compute_in_goal` |
|---|---|---|---|---|
| **G1_bare_miss** `get d K_z = None` (literal 2-elt dict, keys K_type,K_op) | **Timeout / Timeout** (`r_miss_z_bare`) | **Valid (0.07s, 213 steps)** | **Valid (0.37s, 508389 steps)** | **closed by transform** (no prover invoked) |
| G1b_read_hit_first | — | Valid (0.04s, 58) | Valid (0.36s, 544074) | closed by transform |
| G1c_read_hit_second | — | Valid (0.06s, 99) | Valid (0.35s, 549803) | closed by transform |
| G1d_notmem `not (mem_key d K_z)` | — | Valid (0.07s, 168) | **Timeout** (10s) | **closed by transform** (R-A rescues the one Z3 timeout) |
| **walk'vc** (G2, `variant { size v }`) | **Timeout / Timeout** (`walk'vc`) | **Valid (0.07s, 124 steps)** | **Valid (0.02s, 21357 steps)** | Valid (lemma-backed; unaffected) |
| **walk_list'vc** (G2) | Timeout / Timeout (`walk_list'vc`) | **Valid (0.05s, 120)** | **Valid (0.03s, 19852)** | Valid |
| **walk_dict'vc** (G2, the pair-nested VC) | **Timeout / Timeout** (`walk_pairs'vc`) | **Valid (0.06s, 126)** | **Valid (0.02s, 20664)** | Valid |
| walk_fuel'vc (D3 fuel fallback) | — | Valid (0.05s, 131) | Valid (0.03s, 22057) | Valid |
| walk_fuel_list'vc | — | Valid (0.06s, 175) | Valid (0.02s, 20045) | Valid |
| walk_fuel_dict'vc | — | Valid (0.08s, 182) | Valid (0.02s, 20857) | Valid |
| **lemma pack** size_pos'vc | — | Valid (0.09s, 497) | Valid (0.02s, 23133) | Valid |
| size_list_nonneg'vc | — | Valid (0.06s, 239) | Valid (0.02s, 14299) | Valid |
| size_dict_nonneg'vc | — | Valid (0.07s, 248) | Valid (0.02s, 15540) | Valid |
| size_dict_mem'vc | — | Valid (0.07s, 344) | Valid (0.02s, 22208) | Valid |
| **G_probe_large_miss** (11-key nested node) | — | Valid (0.40s, 1776) | Valid (0.19s, 416240) | closed by transform, 0.02 s wall |

### G1 — which mechanism carried it
**Both.** R-B (interned enum keys) makes G1 discharge **bare on both provers**
(constructor disequality, zero string theory). R-A (`compute_in_goal`) additionally
closes the entire G1 family — including `G1d_notmem`, the one goal Z3 could not do
bare — **without invoking any solver at all** (the goal is absent from prover output;
the transformation reduces `get <literal> K_z = None` to `True`). This is the
solver-independence the plan's both-provers criterion rests on.

### G2 — which mechanism carried it
**Direct `variant { size v }`** (route 1) carried G2 on both provers — the
`+1`-per-cons `size` measure + the proven non-negativity pack make every decrease VC
trivial LIA. The **fuel fallback** (route D3, `variant { fuel }` with
`requires { size v <= fuel }`) was built alongside and is **also Valid on both
provers**, so a second independent termination route stands ready for any real walk
shape that resists the direct measure.

---

## 2. Compute-cost probe (D4 guardrail)

Largest realistic schema node = `bignode`: an 11-key dict (every schema key) whose
values include nested `PDict` and a 3-element `PList`. Bare-miss on it
(`get bignode (K_dyn "absent") = None`):

```
$ /usr/bin/time -v why3 prove -a compute_in_goal -P 'Alt-Ergo,2.6.2' -t 10 \
      test-suite/corpus/conformance/spikes/v2_pydict_spike.mlw
  Elapsed (wall clock) time : 0:00.02
  Maximum resident set size : 21460 kbytes
  (G_probe_large_miss absent from prover output -> closed by compute_in_goal)
```

`compute_in_goal` evaluates the whole node and closes the goal in 0.02 s / ~21 MB — no
blowup. Bare (no compute) it is also Valid: Alt-Ergo 0.40 s, Z3 0.19 s. The
schema-bounded fan-out keeps evaluation cheap, as the plan's D4 guardrail predicted.

---

## 3. Negative controls — the 4 false twins (model must still say no)

Restated over the v2 encoding (fixture `V2PyDict`): FT1 miss-is-`Some (PInt 0)`,
FT2 wrong value under a present key, FT3 wrong size arithmetic (drops the `+1`),
FT4 non-member claimed member.

| twin | Alt-Ergo bare | Z3 bare | under `compute_in_goal -a split_vc` |
|---|---|---|---|
| FT1_miss_wrong | Timeout ✓ | Timeout ✓ | Timeout ✓ (evaluates to `False`, not proved) |
| FT2_hit_wrong  | Timeout ✓ | Timeout ✓ | Timeout ✓ |
| FT3_size_wrong (∀ d) | Timeout ✓ | Timeout ✓ | Timeout ✓ (quantified, not evaluable) |
| FT4_notmem_wrong | Timeout ✓ | Timeout ✓ | Timeout ✓ |

All four stay **unproven** on both provers, bare and under the compute+split pipeline.
Crucially `compute_in_goal` does **not** smuggle a false twin through: evaluating a
false concrete goal yields `False` (which no prover proves), and the quantified FT3 is
not fully evaluable — so the transformation is sound as a discharge step. The model can
still say no.

---

## 4. No-axiom assertion

```
$ grep -c '^[[:space:]]*axiom' test-suite/corpus/conformance/spikes/v2_pydict_spike.mlw
0
$ grep -n 'axiom' test-suite/corpus/conformance/spikes/v2_pydict_spike.mlw
3:   ("computation, not axiomatization"; ...)      <- prose
15:     R-C  Everything else is a PROVEN lemma pack — never an `axiom`. ...   <- prose
26:   NO `axiom` keyword anywhere in this file.     <- prose
127:     available to every later VC.  NO axiom.     <- prose
```

Zero `axiom` **declarations** (the 4 tokens are comment prose). The lemma pack
(`size_pos`, `size_list_nonneg`, `size_dict_nonneg`, `size_dict_mem`) is discharged by
`let rec lemma` functions — the recursion IS the induction, each arm's VC is trivial
arithmetic proved by SMT (all Valid on both provers, §1) — i.e. **proved, not
admitted**. Unlike the fmap fixture, the encoding uses only pure inductive datatypes +
the `list` stdlib; it does **not** `use` any axiomatized theory (`fmap.Fmap` /
`set.Fset`), so the trusted base is **not** widened — strictly less than fmap's, not
more.

---

## 5. Why this beats the fmap NO-GO (root-cause)

| fmap failure (phase0 report) | v2 fix | evidence |
|---|---|---|
| `PDict (fmap string pyval)` strict-positivity REJECTED | bespoke inductive `pydict = DNil \| DCons irkey pyval pydict` — no arrow/map in a constructor | typechecks (§1) |
| bare-miss Timeout on both (string theory under recursive unfold) | R-B interned enum keys (constructor disequality) + R-A evaluation | G1 Valid both / closed by compute |
| Z3 Timeout even on int-keyed 2-elt map (abstract `Fmap`/`Fset` theory) | no abstract theory at all — pure inductive + evaluation | G1/probe Valid on Z3 |
| pair-nested `variant` VC Timeout on both | `+1`-per-cons `size` (the head VC was a genuine non-decrease with the additive measure) + proven non-neg pack | walk_dict'vc Valid both |
| fmap has no induction principle → no `size` measure | inductive `pydict` has structural `size` as a logic function; program walk carries `variant { size v }` | walk'vc + fuel both Valid |

---

## 6. Ledger assertions (re-verifiable)

```
$ find src/self-annotate/src -name '*.py' -exec grep -h '\trusted' {} \; | wc -l
1248
$ git status --short src/pycsl/ src/self-annotate/ | grep -v '^??'
(empty — src/pycsl + mirror byte-identical to HEAD)
$ git status --short src/pycsl/proof_axiom_allowlist.py src/self-annotate/src/proof_axiom_allowlist.py
(empty — proof-axiom allow-list untouched)
$ grep -c '^[[:space:]]*axiom' test-suite/corpus/conformance/spikes/v2_pydict_spike.mlw
0
```

- `\trusted` = **1248**, unchanged.
- `src/pycsl` + mirror **byte-identical to HEAD** (no emitter/mirror edit).
- 3-axiom ledger untouched: no `.mlw` axiom declaration; allow-list unchanged; no
  abstract stdlib theory `use`d.
- Tree = this verdict doc + `v2_pydict_spike.mlw` fixture only.

---

## 7. Consequence — Phase 1 is authorized

Phase 0 clears the make-or-break. The wall's SMT/termination core is **not**
research-grade under this encoding: interned keys + computation + a proven lemma pack
discharge both frozen benchmark goals on Alt-Ergo and Z3 with no new axiom, and the
false-twin controls confirm the model is non-vacuous. Per plan §5, **proceed to Phase 1**
(Rocq 8.20 + Lean 4.29 certificates for D1–D3 co-landed with the WhyML theories under
the coupling rule; `irx.py` accessor layer verified against `wf_ir`).

Caveat carried forward (honesty): Phase 0 proves the **encoding kernel** (type,
lemma pack, concrete lookup, program-form termination) — it does **not** yet prove a
whole real Module-6 walker end-to-end. That remains Phase 2's acceptance
(`find_return_type` / `find_named_expr_targets` whole-body-prove), which additionally
needs the emitter routing rules E1–E5 (F1 int-collapse fix, by-ref frame E5) that
Phase 0 deliberately does not touch. The fmap NO-GO is refuted; the integration build
is what Phases 1–2 must still deliver.

### Pointers
- Fixture (committed, `git add -f`): `test-suite/corpus/conformance/spikes/v2_pydict_spike.mlw`
- Beaten NO-GO: `getting-better/tier3/wall-plan-phase0.md`, `getting-better/tier3/fb1-feasibility-spike.md`
- Plan: `generic-dict-str-any-2-plan.md`; problem statement + frozen benchmark: `generic-dict-str-any-2.md` §8
