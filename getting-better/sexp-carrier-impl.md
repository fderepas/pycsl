# sexp-carrier-impl.md — the tuple/sexp value carrier (backlog item-3 reopening cap, count-moving)

Unblocks the `proof2why3/from_sexp.py` cluster (`_const_name`, `_ind_short_name`, `_binder_name` +
their recursive `_find_kername_components`-style helpers) — Python heterogeneous NESTED TUPLES
(sertop s-expressions), which NO existing carrier reaches (pyval's `PArr` is a homogeneous list, not
a positional heterogeneous sexp; lesson-p census confirmed). NECESSARY (unlike R3, which was
redundant with the pre-existing pydict).

## §GATE-S — BOTH make-or-break spikes PASS (oracles in getting-better/sexp-carrier-oracles/)
- **Value model** (`sexp.mlw`): `sexp = SAtom string | SList slist` (recursive), a `last_atom`
  recursive walk (the `_find_kername_components` shape), and total positional `snth` (the `t[i]`
  shape). Positive `pos` Valid (extracts "ker"), evil twin Timeout (non-vacuous), `nth1` Valid,
  axioms 0. z3.
- **Certificate** (`SexpCert.v`): the soundness core — `ssize`/`lsize` measures, `ssize_pos`/
  `lsize_nonneg` well-foundedness, `tail_lt` fold-termination witness, `satom_inj`/`atom_neq_list`
  observability. `coqc` clean; `Print Assumptions` = "Closed under the global context" (AXIOM-FREE)
  for all three load-bearing theorems. Ledger stays 3.

**Disposition: BUILD authorized (spike-proven, axiom-free).** Provability is NOT the wall; the
remaining risk is EMITTER RECOGNITION — can the recognizer lower `isinstance(t,tuple)` → `is_slist`,
`t[i]` → `snth`, and the recursive `_find_kername_components` walk → a `last_atom`-style fold over
the sexp ADT? That is the build's make-or-break falsifier (refutation exit if it walls).

## Build sequence (each its own gate battery; ledger 3; count STRICTLY DOWN per conversion)
1. Certificate: port `SexpCert.v` into a real `Phase2*_Sexp.v` + a `Sexp.lean` (both provers,
   `Print Assumptions`/`#print axioms` clean); wire into `_CoqProject`. Do NOT commit `.vo`/`.olean`.
2. Emitter: sexp theory in `preamble.py` (the `sexp`/`slist` ADT + `snth`/`last_atom`/`is_slist`/
   `atom_of` projectors), gated on a corpus-absent sentinel (byte-inert).
3. Recognizer: lower the from_sexp tuple-walk shape (isinstance-tuple dispatch + positional index +
   recursive helper walk) onto the sexp ADT. Convert the from_sexp cluster (the 3 + helpers) that
   the recognizer reaches; count DOWN.
Refutation exit: if the emitter cannot lower the tuple-walk onto the ADT → CERTIFIED-BOUNDARY,
record the exact recognizer blocker, revert clean, fall through to the next backlog item.

## §OUTCOME — 2026-07-24 driver run: CERTIFIED-BOUNDARY (cert proven, emitter cannot lower)

**Verdict: the certificate stands, the recognizer (step 3) WALLS. Nothing committed (cert + emitter
would be dead infra — nothing in the corpus/mirror emits the sexp theory), tree left clean.** Count
holds at 942. Refutation exit taken per the make-or-break clause; NO grind, NO body-rewrite/truncation.

### Certificate re-verified INDEPENDENTLY (driver, not on spike trust) — both planes green
- `SexpCert.v` re-built in a clean scratch dir with coqc **8.20.1**: exit 0, `Print Assumptions` on all
  three load-bearing theorems (`ssize_pos`, `lsize_nonneg`, `tail_lt`) = **"Closed under the global
  context"** (AXIOM-FREE). Ledger would stay 3.
- `sexp.mlw` re-proved with why3 1.8.2 / z3: `pos` **Valid** (0.01s, extracts "ker"), `evil` **Timeout**
  (5s, non-vacuous), `nth1` **Valid** (0.01s). 0 axioms. Provability is NOT the wall (as the spike said).

### The recognizer WALL — three concrete blockers on the VERBATIM from_sexp bodies
The 3 targets (`_const_name`, `_ind_short_name`, `_binder_name`) + the helper chain they need
(`_find_kername_components`, `_walk_kername`, `_walk_modpath`) cannot be lowered onto the sexp ADT
because the LIVE bodies (which a conversion must port BYTE-VERBATIM — lesson j/§10.12) do this:

- **BLOCKER 1 — heterogeneous positional index `t[i]` (the make-or-break).** `snth children(t) i` has
  ONE WhyML type: `sexp`. But the SAME syntactic form `t[i]` is consumed as a **string** at
  `out.append(iid[1])`, `return inner[1]`, `field[0] == "binder_name"`, AND as a **sub-sexp** at
  `_walk_modpath(mp[1])`, `_find_kername_components(sub)`. The declared signatures fix the string sites'
  types (`-> Optional[str]`, `out: List[str]`), so a uniform-sexp model breaks at the signature boundary
  and the string sites REQUIRE an inserted `atom_of` projector — a **per-occurrence, consuming-context-
  directed coercion** the emitter does not have. Its subscript lowering (`expressions.py`) is
  emit_ir-typed-NODE projection only (`IrSub`, fixed keys `["value"/"index"/"object"]`, fixed element
  types) — there is no arbitrary-positional-index-into-heterogeneous-tuple path, and no return/target-
  type-directed coercion at subscript sites. This is a new type-inference capability, not a recognizer.

- **BLOCKER 2 — the verbatim helpers build a `List[str]` result the certified oracle SIDESTEPS.**
  `_walk_kername`/`_walk_modpath`/`_find_kername_components` accumulate `out: List[str]` via
  `out.append(...)`, `out.extend(_walk_modpath(mp))`, `out.extend(reversed(segs_reversed))`, iterating
  `for seg in segments` / `for sub in payload`. That is a SECOND value model (mutable string-list result
  + `reversed`) composed WITH the sexp walk. The proven oracle `last_atom` returns ONE string and
  computes only the final answer — it does NOT model the components-list the verbatim bodies build. So
  the certificate covers a SIMPLER projection than the bodies a conversion must port; the port needs
  List[str]-accumulation + `reversed` + for-over-slist machinery the oracle never certified.

- **BLOCKER 3 — string-literal tag dispatch + length guards.** `t[0] == "KerName"`, `len(t) >= 3`
  must lower to `atom_of(snth …) = "KerName"` + an slist-length guard. Buildable in principle, but adds
  to a surface already blocked by 1 & 2.

The existing `generic_fold.py` recognizer REJECTS these (precision-over-recall): it keys on
`isinstance(_, dict/list)` descending pydict/pyval and accumulates into a **by-reference Set/dict**
param (`writes { acc }`) — the from_sexp shape is `isinstance(_, tuple)`, **positional** index, and a
**returned List[str]**, matching none of it.

### What would REOPEN it (for a future ladder edit)
A bespoke sexp recognizer would have to BUILD, minimally: (a) consuming-context-directed `atom_of`
coercion at heterogeneous `t[i]` sites keyed off the target/return type (BLOCKER 1 — the hard one, a
type-inference feature); (b) a `List[str]` (`seq string`) accumulator model with `.append`/`.extend`/
`reversed` composed over a for-fold on the slist spine (BLOCKER 2); (c) positional-tag dispatch +
slist-length guards (BLOCKER 3). That is a multi-feature, session-scale build for 3 stubs (net −3) —
the same §10.3 generic-Any-tree-walker class, sharpened here to "heterogeneously-typed tuple positions
consumed context-dependently." Deprioritized; the certificate + value oracle are banked in
`getting-better/sexp-carrier-oracles/` (proven, reusable) for whenever that build is authorized.

## §OUTCOME-2 — 2026-07-24 driver REOPEN (GATE-S net accounting + pyval-reuse) — REFINED [COST/SCALE] BOUNDARY

**Verdict: boundary STANDS, but the record is materially improved on two axes and the cost is LOWER
than §OUTCOME recorded. Count holds at 941; tree clean; nothing committed (still no bounded, non-facade,
count-moving entry).** The reopen ran GATE-S (net accounting FIRST, per the giants-net-marker trap) then
a concrete verbatim spike of `_const_name`.

### Finding 1 — NET ACCOUNTING: net is POSITIVE, NOT a giants-trap (§10.7 concern REFUTED)
The recognizer is LIVE-emitter code that lands in `src/pycsl/module6_whyml/generic_fold.py`, which is
**NOT in the self-annotate mirror** (`ls src/self-annotate/src/module6_whyml/` has no `generic_fold.py`;
precedent: the `recognize_named_field_existence` + `emit_named_field_existence_group` additions for
`_pattern_has_constructor` added **0** mirror stubs). The mirror-check is a declared SUBSET gate — it
verifies each MIRROR def has a source counterpart, NOT that each source def is mirrored — so new
source-only recognizer/emitter methods force **zero** new `\trusted` mirror stubs. NET = (3 stubs
converted) − (0 new stubs) = **+3** (count −3). The prior "net −3" is a genuine count DECREASE, not
surface growth. So this is NOT the giants-are-net-marker-positive trap; the deprioritization was never
about net-marker-negativity.

### Finding 2 — pyval REUSE eliminates the new-ADT + new-certificate cost (supersedes build-step 1)
The certified `pyval` ADT already in `preamble.py` (`_pydict_theory_lines`) IS the sexp carrier:
`type pyval = PInt | PStr string | PBool | PNone | PList (list pyval) | PDict pydict` with `is_pstr`/
`is_plist` projectors, the `pv_size` measure, and PROVEN axiom-free `size_pos`/`size_list_nonneg` lemmas.
Map `SAtom s → PStr s`, `SList xs → PList xs`, `is_slist → is_plist`. The build needs only **3 small
total projectors** — `pv_nth : pyval→int→pyval`, `pv_len : pyval→int`, `atom_of : pyval→string` — added
to the EXISTING pyval theory. **No separate `sexp` ADT, no `Phase2*_Sexp.v`/`Sexp.lean`, no new
certificate** (the pyval cert already covers measure/termination); ledger stays 3 trivially and Why3
already accepts pyval. Build-sequence step 1 (port SexpCert.v into new cert files) is therefore
UNNECESSARY. The banked `sexp-carrier-oracles/` remain valid but encode the SEPARATE-ADT approach that
pyval-reuse supersedes.

### Finding 3 — the residual wall, precisely located and classified [COST/SCALE] (not correctness)
Concrete spike (verbatim `_const_name` ported into the mirror, `--no-proof --keep-mlw`): the current
emitter lowers it VACUOUSLY (`const_node: int`, `isinstance_op 0 0` on HASH CONSTANTS) AND fails L3-tc
(the `Optional[str]` return-union `Arm_0_0 string | Arm_0_None` cannot absorb `subscript_get`'s `int`).
The gap to a non-vacuous lowering is the §10.3 value-returning-pyval-walker subsystem — the SAME class as
driver-backlog item 3 (itself CERTIFIED-BOUNDARY). No bounded single-feature entry point exists:
- `_const_name` / `_ind_short_name`: their OWN bodies are clean of BLOCKER 1 (the `[i]` is used only as a
  sub-sexp fed to the trusted helper), BUT the trusted helper `_find_kername_components` emits as
  `val (payload: int) : array string`. Typing `const_node` pyval makes `payload = pv_nth const_node 1 :
  pyval`, which cannot be passed to a `payload: int` param. There is **no param-annotation→pyval hook**
  (pyval is inferred from usage; a trusted stub has none). So converting these two requires EITHER a new
  annotation→pyval-param mechanism OR converting `_find_kername_components` — which carries BLOCKER 1
  (`out.append(iid[1])` string-coercion alongside `_walk_modpath(mp[1])` sub-sexp at the same `[1]`) +
  BLOCKER 2 (`List[str]` via `.append`/`.extend`/`reversed`). Also `parts[-1]` mis-lowers to literal
  index `-1` (negative-from-end unmodeled) — a further small gap.
- `_binder_name`: self-contained (no helper call, no BLOCKER 2), but needs a value-returning pyval-list
  `for field in binder_annot` fold with EARLY RETURN of `inner[1]` (option string) + BLOCKER 1 `atom_of`
  coercion at the nested tag sites (`field[0]=="binder_name"`, `val[0]=="Name"`, `inner[0]=="Id"`).
All of these are **sound** (`atom_of`/`pv_nth`/`pv_len` are total projections; the guards make the
coercion faithful; no unsound guess, no 4th axiom, Why3 accepts the carrier) — so **[COST/SCALE]**, not
correctness. A recognizer firing only on these exact nested shapes is a Gate-C facade reject (§10.10);
the genuine build is the general value-returning-pyval-walker (backlog item 3). No count-moving,
non-facade increment was available in-window, so nothing was committed (committing dead projector infra
was already rejected in §OUTCOME).

**REOPEN (revised, for a future ladder edit):** build on pyval REUSE (Finding 2) — add `pv_nth`/`pv_len`/
`atom_of` to the pyval theory (no new cert), then the §10.3 general value-returning-pyval walker with
(a) context-directed `atom_of` coercion at `==<strlit>` / str-return sites, (b) a param-annotation→pyval
hook so a trusted helper can carry a pyval param (unblocks `_const_name`/`_ind_short_name` without
converting the helper), (c) negative-index-from-end lowering. This is the same subsystem backlog item 3
needs; do it once, generally, and the from_sexp cluster falls out.
